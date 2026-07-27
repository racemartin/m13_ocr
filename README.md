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
| Base vectorielle | Milvus |
| Persistance | MongoDB |
| Moteur d'échecs | Stockfish (NNUE) |
| Gestionnaire de paquets Python | `uv` |
| Orchestration | Docker Compose |

## Prérequis

- Git
- **Docker Desktop** installé sur Windows, avec le backend **WSL2**
  activé (Docker Desktop → Settings → General → *Use the WSL 2 based
  engine*, puis Settings → Resources → WSL Integration → activer la
  distribution utilisée pour lancer les commandes).
- Docker Desktop doit être **démarré manuellement** (c'est une
  application graphique, elle ne se lance pas toute seule) avant
  d'exécuter la moindre commande `docker`.
- (uniquement pour le développement local hors conteneur, optionnel)
  [`uv`](https://docs.astral.sh/uv/) installé sur le poste.
- (à partir de l'étape 5) Node.js et Angular CLI.

> **`uv` n'est requis que si tu veux lancer les tests, le linter ou
> l'auto-complétion de l'IDE en dehors de Docker.** Le `Dockerfile`
> installe `uv` et toutes les dépendances **à l'intérieur** du
> conteneur automatiquement à l'étape "build" ; il n'y a rien à
> installer manuellement pour lancer l'application via
> `docker compose`.

## Étape 0 — Initialiser le dépôt local

Ce dépôt n'existe encore qu'en local (aucun `git clone` possible pour
l'instant, aucun remote créé) :

```bash
# Depuis le dossier contenant les fichiers du scaffold
git init
git add .
git commit -m "Etape 1 : structure initiale + backend Hello World"
```

Si tu crées ensuite un dépôt distant (GitHub, GitLab...) :

```bash
git remote add origin <url-du-depot>
git push -u origin main
```

## Installation et démarrage (via Docker — recommandé)

Toutes les commandes ci-dessous s'exécutent **depuis la racine du
projet** (là où se trouve `docker-compose.yml`), pas depuis
`backend/`.

```bash
# 1. Vérifier que Docker Desktop est bien démarré et accessible
docker info

# 2. Créer le fichier d'environnement local
cp .env.example .env

# 3. Construire l'image et lancer les services
#    (uv installe les dependances DANS le conteneur a ce moment-la)
docker compose up --build
```

Vérifier que le backend répond (dans un autre terminal) :

```bash
curl http://localhost:8000/api/v1/healthcheck
```

Réponse attendue :

```json
{"status": "ok", "application": "FFE Chess Agent - Backend", "version": "0.1.0"}
```

## Développement local sans Docker (optionnel)

Utile pour l'auto-complétion, `mypy`, `ruff` ou `pytest` directement
dans l'IDE, sans passer par le conteneur :

```bash
cd backend
uv sync                 # installe l'environnement virtuel local
uv run pytest           # execute les tests
uv run ruff check app/  # verifie le style
```

Ceci n'est **pas** une étape nécessaire pour que
`docker compose up --build` fonctionne — les deux méthodes sont
indépendantes.

## Structure du dépôt

```
.
├── backend/            # API FastAPI + agent LangGraph (Python, uv)
│   ├── app/
│   │   ├── api/v1/      # Routes REST
│   │   ├── core/        # Configuration (variables d'environnement)
│   │   └── main.py       # Point d'entrée de l'application
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/            # Application Angular (à partir de l'étape 5)
├── docs/
│   └── ARCHITECTURE.md  # Architecture cible + diagrammes PlantUML
├── docker-compose.yml
├── .env.example
└── README.md
```

## Avancement de la mission

| Étape | Contenu | Statut |
|---|---|---|
| 1 | Environnement de dev, `docker-compose.yml`, healthcheck | ✅ en cours |
| 2 | Agent LangGraph : endpoints `/moves/{fen}` et `/evaluate/{fen}` | à venir |
| 3 | RAG Milvus sur Wikichess | à venir |
| 4 | Intégration API YouTube | à venir |
| 5 | Interface Angular (`ngx-chessboard`) | à venir |
| 6 | Containerisation complète + démo | à venir |
| 7 | Étude de faisabilité : système MCP d'analyse vidéo (conception) | à venir |

## Points de vigilance

- Les versions de Python (3.12) et Node.js sont figées dans les
  `Dockerfile` respectifs pour garantir la reproductibilité.
- Les ports exposés (`BACKEND_PORT`, `FRONTEND_PORT`) sont
  configurables via `.env` pour éviter tout conflit avec d'autres
  services déjà en cours sur la machine hôte.
