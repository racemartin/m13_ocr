<p align="center">
  <img src="../docs/logo_ffe.png" alt="Fédération Française des Échecs" width="120">

  # FFE Chess Agent
  **Mise en place un Agent IA pour l'apprentissage des échecs**

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2-1C3C3C)](https://langchain-ai.github.io/langgraph/)
[![Milvus](https://img.shields.io/badge/Milvus-2.4-00A1EA)](https://milvus.io)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248)](https://www.mongodb.com)
[![Angular](https://img.shields.io/badge/Angular-18-DD0031)](https://angular.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)](https://www.docker.com)

</p>

API FastAPI et agent LangGraph du POC "Agent IA pour l'apprentissage
des échecs" (FFE). Voir le [`README.md`](../README.md) et
[`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) à la racine du
dépôt pour le contexte complet, l'installation et l'architecture.

**Documents complémentaires :**
- [Support de présentation (M13)](../docs/Suport_de_presentation-M13_Developpez_un_agent_IA_pour_lapprentissage_des_echecs.pdf)
- [Étude de faisabilité MCP](../docs/Etude_de_faisabilite_V1.pdf)

# Structure

```
app/
├── main.py                  Point d'entree FastAPI
├── api/v1/                  Presentation : routers + schemas Pydantic
├── application/              Cas d'utilisation (orchestrent les ports)
├── domaine/
│   ├── modeles.py            Structures de donnees du metier
│   └── ports/                 Contrats (interfaces) du domaine
├── infrastructure/            Adaptateurs concrets (python-chess,
│                               Lichess, Stockfish)
└── core/
    └── dependances.py         Cablage FastAPI <-> ports <-> adaptateurs
```

## Lancer le backend en local (sans Docker)

```bash
uv sync
uv run uvicorn app.main:application --reload
```

Nécessite le binaire Stockfish installé sur la machine (`apt-get install
stockfish` sous Debian/Ubuntu, ou définir `STOCKFISH_PATH` dans `.env`
si le binaire se trouve ailleurs).

## Tests automatisés (pytest)

```bash
uv sync --group test
uv run pytest -v
```

Les tests des endpoints `/moves` et `/evaluate` utilisent des **doublures
de test** (`tests/fakes.py`) injectées via `dependency_overrides` : ils
ne font aucun appel réseau vers Lichess et ne nécessitent pas Stockfish.

## Script de vérification manuelle des endpoints

À lancer contre un backend déjà démarré (Docker ou `uv run uvicorn`) :

```bash
uv run python scripts/test_endpoints.py
uv run python scripts/test_endpoints.py --base-url http://localhost:8081

curl "https://explorer.lichess.ovh/masters?fen=rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20w%20KQkq%20-%200%201"

```

Vérifie successivement `/healthcheck`, `/moves/{fen}` (position théorique
et FEN invalide) et `/evaluate/{fen}`, avec un résumé OK/ÉCHEC par test.
