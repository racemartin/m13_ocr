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
- Docker et Docker Compose installés sur le poste
- (à partir de l'étape 5) Node.js et Angular CLI

## Installation et démarrage

```bash
# 1. Cloner le dépôt
git clone <url-du-depot>
cd ffe-chess-agent

# 2. Créer le fichier d'environnement local
cp .env.example .env

# 3. Lancer les services (étape 1 : backend uniquement)
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

Depuis un poste local avec un navigateur:

```bash
http://192.168.1.146:8081/api/v1/healthcheck
```


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
