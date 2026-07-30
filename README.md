# Agent IA pour l'apprentissage des échecs — FFE (POC)

## Objectif

POC (Proof of Concept), développé en 2 semaines pour la Fédération
Française des Échecs (FFE), d'un agent intelligent qui accompagne les
jeunes espoirs dans l'apprentissage des **ouvertures d'échecs** :
coups théoriques (Lichess), évaluation de position (Stockfish),
contexte sur l'ouverture (RAG Wikichess via Milvus) et vidéos
explicatives (YouTube), le tout via un échiquier interactif Angular.

L'architecture cible complète (composants, services Docker, services
externes, choix techniques) est détaillée dans
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).


## Stack technique

| Couche | Technologie |
|---|---|
| Frontend | Angular + `ngx-chessboard` |
| Backend | FastAPI + LangGraph |
| Règles du jeu / validation FEN | `python-chess` |
| Moteur d'évaluation | Stockfish (binaire natif + wrapper Python `stockfish`) |
| Théorie des ouvertures | API Lichess (Opening Explorer) |
| Base vectorielle | Milvus |
| Persistance | MongoDB |
| Gestionnaire de paquets Python | `uv` |
| Orchestration | Docker Compose |

## Architecture (vue Docker)

```bash
+-----------------------------------------------------------------------+
| Poste de developpement (Docker Compose)                               |
|                                          port 8081                    |
|                       +-----------------------------+                 |
|                       |      Conteneur frontend     |                 |
|                       | Angular (nginx ou ng serve) |                 |
|                       +-----------------------------+                 |
|                                        | port 8000 (reseau docker)    |
|                                        |                              |
| +------------------------------------+ |                              |
| |   Stockfish n'est PAS un service   | |                              |
| |  Docker a part : binaire installe  | |                              |
| | dans l'image du conteneur backend, | |                              |
| |     appele en sous-processus.      | |                              |
| +------------------------------------+ v                              |
|                    +---------------------+ HTTPS +-------------+      |
|                    | Conteneur backend   |-----> | Lichess API |      |
|                    | FastAPI + Uvicorn   |       +-------------+      |
|                    | + Agent LangGraph   | HTTPS +------------------+ |
|                    |                     |-----> | YouTube Data API | |
|                    +---------------------+       +------------------+ |
|                    | port 19530         | port 27017                  |
|                    v                    v                             |
|     +-----------------------------+    +-------------------+          |
|     | Conteneur milvus-standalone |    | Conteneur mongodb |          |
|     |            Milvus           |    |      MongoDB      |          |
|     +-----------------------------+    +-------------------+          |
|             | metadonnees       | stockage objets                     |
|             |                   |                                     |
|             v                   v                                     |
|     +----------------+  +-----------------+                           |
|     | Conteneur etcd |  | Conteneur minio |                           |
|     +----------------+  +-----------------+                           |
+-----------------------------------------------------------------------+
```

## Prérequis

- Git
- Docker et Docker Compose installés sur le poste
- (à partir de l'étape 5) Node.js et Angular CLI



## Installation et démarrage

```bash
# 1. Cloner le dépôt
git clone <url-du-depot>
cd ffe-chess-agent

# 2. Créer le fichier d'environnement local
cp .env.example .env

# 3. Lancer les services
docker compose up --build
```

Vérifier que le backend répond :

```bash
curl http://localhost:8000/api/v1/healthcheck
```

Réponse attendue :

```json
{"status": "ok", "application": "FFE Chess Agent - Backend", "version": "0.1.0"}
```

Depuis un autre poste du réseau local (remplacer par l'IP de la
machine hôte) :

 A travers du frontend avec la App Angular (port 8081):
```
http://192.168.1.146:8081/api/v1/healthcheck
```

Directement au backend dans la API (port 8000):
```
http://192.168.1.146:8000/docs
```


## Tester les endpoints de l'étape 2

Deux nouveaux endpoints exposent la logique de l'agent :

- `GET /api/v1/moves/{fen}` — coups théoriques connus par Lichess
- `GET /api/v1/evaluate/{fen}` — évaluation Stockfish (centipawns / mat)

**Tests automatisés (pytest)**, sans appel réseau ni binaire
Stockfish nécessaire (adaptateurs remplacés par des doublures de
test) :

```bash
cd backend
uv sync --group test
uv run pytest -v
```

**Script de vérification manuelle**, à lancer contre un backend déjà
démarré (Docker ou local) :

```bash
cd backend
uv run python scripts/test_endpoints.py --base-url http://localhost:8000
uv run python scripts/test_endpoints.py --base-url http://localhost:8081
```

Détails complets (structure des tests, doublures, options du script)
dans [`backend/README.md`](backend/README.md).

> ⚠️ **Point de vigilance connu** : le service public
> `explorer.lichess.ovh` (Opening Explorer) traverse une panne
> d'infrastructure côté Lichess depuis fin février 2026. Tant qu'elle
> dure, `/moves/{fen}` répond `200` avec une liste vide au lieu des
> coups théoriques réels — c'est le comportement de dégradation
> gracieuse voulu (voir `AdaptateurLichess`), pas un bug côté agent.
> `/evaluate/{fen}` n'est pas concerné (ne dépend que de Stockfish,
> exécuté localement dans le conteneur).



## Étape 3 — Pipeline d'ingestion RAG

Pour construire le corpus vectorisable (`data/corpus/*.md`), un pipeline en 3 scripts, chacun source-consciente sauf le dernier :

```
data/seeds/*.csv (curés à la main)
        |
        v
scripts/ingestion/fetch_wikichess.py    scripts/ingestion/fetch_wikipedia.py
        |                                        |
        v                                        v
data/raw/wikichess/*.json               data/raw/wikipedia/*.json
        |                                        |
        +------------------+---------------------+
                            v
             scripts/ingestion/build_corpus.py
                            |
                            v
                   data/corpus/*.md
```

### Exécution

```bash
cd backend
python scripts/ingestion/fetch_wikichess.py
python scripts/ingestion/fetch_wikipedia.py
python scripts/ingestion/build_corpus.py
```

### Indexation et vérification

Une fois le corpus généré (`data/corpus/*.md`), indexe-le dans Milvus puis vérifie :

```bash
uv run python scripts/ingestion/indexer_corpus.py
uv run python scripts/ingestion/diagnostic_milvus.py
```

> ⚠️ **Point d'attention** : ces scripts, lancés depuis la machine hôte
> (pas depuis un conteneur), doivent utiliser `MILVUS_HOST=localhost`
> (le service Docker n'est résolu par son nom `milvus-standalone` que
> *depuis l'intérieur* du réseau Docker) :
> ```powershell
> $env:MILVUS_HOST="localhost"
> uv run python scripts/ingestion/indexer_corpus.py
> ```
> Le backend, lui, tourne dans le réseau Docker et résout
> `milvus-standalone` sans configuration supplémentaire.

> ⚠️ **`data/raw/` et `data/corpus/` sont dans `.gitignore`** — ce sont
> des artefacts régénérables (JSON bruts, HTML de debug, corpus
> normalisé), pas du code source. Seul `data/seeds/*.csv` (les listes
> curées à la main) est versionné.

### Schéma commun des données brutes

Les deux scripts de fetch écrivent un JSON par article, avec exactement les mêmes clés (`modele_brut.DonneeBrute`) :
```json
{
  "source": "wikichess" | "wikipedia",
  "nom": "...", "categorie": "...", "url": "...", "langue": "en" | "fr",
  "extrait": "...", "metadonnees": {}, "recupere_le": "..."
}
```

### Points de vigilance découverts en conditions réelles

- **API Wikimedia** : exige un `User-Agent` descriptif (nom du projet + contact) — sans lui, `403 Forbidden` systématique. Confirmé empiriquement : 165/165 échecs sans ce header, résolu en l'ajoutant.
- **Wikichess** : le contenu narratif n'est pas repéré par un motif de texte global, mais par l'élément DOM `<div align="justify">` — il en existe plusieurs par page (menu, footer...), donc seul celui contenant le séparateur `====` est retenu. Selon les pages, la prose se trouve avant `====`, après la ligne `Contributors :`, les deux, ou aucune (page purement statistique, cas normal — pas un bug).
- Chaque page Wikichess en échec sauvegarde son HTML brut dans `data/raw/_debug/` pour inspection, sans bloquer le traitement des autres.
- Traçabilité complète via LogTool (mêmes conventions que le reste du backend) : chaque script journalise ses paramètres, le détail de la première entrée traitée (utile pour diagnostiquer sans script séparé), et le compte final réussies/échouées.


## Tester l'endpoint de l'étape 3 (RAG)

```bash
curl "http://localhost:8000/api/v1/vector-search?q=sicilienne&top_k=3"
```

Réponse attendue (`200`) :
```json
[
  {
    "texte": "...",
    "ouverture": "Défense sicilienne",
    "source_url": "https://fr.wikipedia.org/wiki/...",
    "score": 0.87
  }
]
```

Une liste vide est une réponse valide (aucun contexte pertinent trouvé),
pas une erreur.


## Structure du dépôt

```
.
├── backend/                 # API FastAPI + agent LangGraph (Python, uv)
│   ├── app/
│   │   ├── api/v1/           # Presentation : routes REST + schemas
│   │   │   ├── healthcheck.py
│   │   │   ├── moves.py       # GET /moves/{fen}
│   │   │   ├── evaluate.py    # GET /evaluate/{fen}
│   │   │   └── schemas.py
│   │   ├── domaine/           # Modeles + ports (contrats), sans dependances
│   │   │   ├── modeles.py
│   │   │   └── ports/
│   │   ├── application/       # Cas d'utilisation (orchestrent les ports)
│   │   ├── infrastructure/    # Adaptateurs concrets (python-chess,
│   │   │                       Lichess, Stockfish)
│   │   ├── core/              # Configuration + cablage des dependances
│   │   └── main.py            # Point d'entree de l'application
│   ├── tests/                 # Tests pytest (doublures des ports)
│   ├── scripts/                # Script de verification manuelle des endpoints
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                 # Application Angular (à partir de l'étape 5)
├── docs/
│   └── ARCHITECTURE.md       # Architecture cible + diagrammes PlantUML
├── docker-compose.yml
├── .env.example
└── README.md
```

## Avancement de la mission

| Étape | Contenu | Statut |
|---|---|---|
| 1 | Environnement de dev, `docker-compose.yml`, healthcheck | ✅ terminé |
| 2 | Agent : endpoints `/moves/{fen}` et `/evaluate/{fen}` (python-chess, Lichess, Stockfish) | ✅ terminé |
| 3 | RAG Milvus : ingestion (Wikichess + Wikipedia), indexation, `/vector-search` | 🚧 en cours (LangGraph pas encore intégré) |
| 4 | Intégration API YouTube | à venir |
| 5 | Interface Angular (`ngx-chessboard`) | à venir |
| 6 | Containerisation complète + démo | à venir |
| 7 | Étude de faisabilité : système MCP d'analyse vidéo (conception) | à venir |


| # | Service | Étape | Statut | Commande de test |
|---|---|---|---|---|
| 1 | **Notre API** (backend FastAPI) | 1 | ✅ implémenté | `curl http://localhost:8000/api/v1/healthcheck` |
| 2 | **python-chess** (validation FEN) | 2 | ✅ implémenté | `curl http://localhost:8000/api/v1/moves/ceci-nest-pas-un-fen` *(attend 422)* |
| 3 | **Stockfish** | 2 | ✅ implémenté | `curl http://localhost:8000/api/v1/evaluate/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20w%20KQkq%20-%200%201` |
| 4 | **Lichess API** | 2 | ✅ implémenté (service externe en panne) | `curl http://localhost:8000/api/v1/moves/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20w%20KQkq%20-%200%201` |
| 4b | ↳ Lichess en direct (sans passer par notre API) | — | diagnostic | `curl "https://explorer.lichess.ovh/masters?fen=rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20w%20KQkq%20-%200%201"` |
| 5 | **LangGraph** (orchestration de l'agent) | 3 | ⏳ à venir | *(pas de commande pour l'instant — sera testé via l'endpoint qui l'utilisera, une fois implémenté)* |
| 6 | **etcd** (métadonnées de Milvus) | 3 | ✅ implémenté | `docker compose exec etcd etcdctl endpoint health` |
| 7 | **minio** (stockage objets de Milvus) | 3 | ✅ implémenté | `curl -I http://localhost:9002/minio/health/live` *(port remappé)* |
| 8 | **Milvus** | 3 | ✅ implémenté | `curl http://localhost:9091/healthz` |
| 8b | ↳ Diagnostic du contenu indexé | 3 | ✅ implémenté | `uv run python scripts/ingestion/diagnostic_milvus.py` |
| 9 | **YouTube API** | 4 | ⏳ à venir | `curl "https://www.googleapis.com/youtube/v3/search?part=snippet&q=chess+opening&key=$Env:YOUTUBE_API_KEY"` |
| 10 | **MongoDB** | 6 | ⏳ à venir | `mongosh "mongodb://localhost:27017" --eval "db.runCommand({ ping: 1 })"` |



## Points de vigilance

- Les versions de Python (3.12) et Node.js sont figées dans les
  `Dockerfile` respectifs pour garantir la reproductibilité.
- Les ports exposés (`BACKEND_PORT`, `FRONTEND_PORT`) sont
  configurables via `.env` pour éviter tout conflit avec d'autres
  services déjà en cours sur la machine hôte.
- Le binaire Stockfish est installé dans l'image Docker du backend
  (`apt-get install stockfish`) ; en local hors Docker, il doit être
  installé séparément ou `STOCKFISH_PATH` défini dans `.env`.
- Les appels à des API externes (Lichess, puis YouTube à l'étape 4)
  sont volontairement tolérants aux pannes : une indisponibilité
  externe ne doit jamais faire planter l'agent, seulement dégrader la
  réponse (voir note ci-dessus sur l'étape 2).

  ### Résilience de `/moves/{fen}` : repli local Polyglot

Pour ne pas dépendre uniquement de la disponibilité de Lichess (voir
panne documentée ci-dessus), l'endpoint `/moves/{fen}` utilise un
adaptateur composite avec repli automatique :

1. Tente d'abord l'**API Lichess** (Opening Explorer).
2. Si elle échoue ou renvoie une liste vide, retombe sur un **livre
   Polyglot local** (`data/polyglot/livre_ouvertures.bin`), lu sans
   aucun appel réseau — donc jamais indisponible.

```bash
GET /api/v1/moves/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20w%20KQkq%20-%200%201
```
```json
[
  {"uci": "e2e4", "san": "e4", "nombre_parties": 1},
  {"uci": "d2d4", "san": "d4", "nombre_parties": 1},
  {"uci": "c2c4", "san": "c4", "nombre_parties": 1}
]
```

> ⚠️ **Point d'attention** : pour les entrées venant du livre Polyglot,
> `nombre_parties` n'est **pas** un nombre de parties réelles (contrairement
> à Lichess) mais le *poids* (`weight`) assigné par le livre à ce coup —
> réutilisé par simplicité dans le même champ du modèle de domaine.

Le livre ne couvre que les lignes d'ouverture connues ; au-delà, il
renvoie aussi une liste vide (comportement identique à Lichess), donc
la logique de repli vers Stockfish (étape 3/4) reste cohérente.

Variable d'environnement optionnelle (`.env`) :
```properties
POLYGLOT_BOOK_PATH=
```
Laissée vide, le code retombe automatiquement sur
`data/polyglot/livre_ouvertures.bin` (chemin par défaut résolu dans
`app/core/dependances.py`).

### Réponse enrichie de `/evaluate/{fen}`

Depuis l'étape 2, `/evaluate/{fen}` ne retourne plus seulement un score
brut : la réponse inclut aussi le coup recommandé par Stockfish, la
profondeur de recherche utilisée, et le FEN en écho (utile pour tracer
plusieurs appels en parallèle dans les logs).

```bash
GET /api/v1/evaluate/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20w%20KQkq%20-%200%201
```
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "evaluation": {
    "type": "cp",
    "valeur": 39,
    "score": "+0.39"
  },
  "coup_recommande": "e2e4",
  "profondeur": 15
}
```

> ⚠️ **Décision en attente** : les champs sont actuellement nommés en
> français (`valeur`, `coup_recommande`, `profondeur`), cohérent avec le
> reste de l'API (`nombre_parties`, etc.). Si le frontend Angular ou un
> client externe attend des noms anglais (`value`, `best_move`, `depth`),
> il faudra renommer les champs dans `app/api/v1/schemas.py` avant
> l'étape 5 — c'est un changement isolé à ce seul fichier.


---

## Auteur

**Rafael Cerezo Martín**

- Email : [rafael.cerezo.martin@icloud.com](mailto:rafael.cerezo.martin@icloud.com)
- GitHub : [@racemartin](https://github.com/racemartin)

---

## Licence

MIT License — voir [LICENSE](LICENSE) pour les détails.
