# ############################################################################
# Point d'entree pour LangGraph Studio -- graphe AVEC les services reels
# ############################################################################
# A la difference de studio_graph.py (doublures), ce module reutilise les
# VRAIES fabriques de production (dependances.py) : vrai appel Lichess,
# vrai Stockfish, vraie recherche vectorielle Milvus. Seul le checkpointer
# est remplace par un MemorySaver, pour ne jamais ecrire dans le MongoDB
# de production pendant une exploration dans Studio.
#
# Prerequis pour que CE module fonctionne (contrairement a studio_graph.py,
# qui n'en a aucun) :
#   - Stockfish installe et accessible localement (STOCKFISH_PATH dans .env,
#     ou binaire dans le PATH) -- pas seulement dans l'image Docker.
#   - Milvus accessible depuis l'hote (MILVUS_HOST=localhost si le port
#     est expose par docker-compose.yml).
#   - .env charge (deja garanti par load_dotenv() dans dependances.py).

from langgraph.checkpoint.memory import MemorySaver

from app.core.dependances import (
    obtenir_service_coups_theoriques,
    obtenir_service_evaluation,
    obtenir_service_recherche_contexte,
)
from app.application.agent.graphe_agent import construire_graphe

graph = construire_graphe(
    service_coups      = obtenir_service_coups_theoriques(),
    service_evaluation  = obtenir_service_evaluation(),
    service_contexte    = obtenir_service_recherche_contexte(),
    checkpointer         = MemorySaver(),   # Jamais le Mongo de production ici
)
