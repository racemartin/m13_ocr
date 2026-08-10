# ############################################################################
# Point d'entree de l'application FastAPI
# ############################################################################
# Ce module cree l'instance FastAPI et enregistre les routeurs de l'API.
# La logique metier ne vit jamais ici : ce fichier est un adaptateur
# d'entree (driving adapter) qui expose la couche domaine via HTTP.

# Bibliotheque standard
import time                       # Mesure de la duree du prechauffage
from   contextlib import asynccontextmanager    # Gestionnaire de lifespan

# Bibliotheques tierces
from   fastapi import FastAPI    # Framework web ASGI

# Modules internes
from   app.api.v1 import healthcheck    # Route de verification de sante
from   app.api.v1 import moves          # Route des coups theoriques
from   app.api.v1 import evaluate       # Route d'evaluation de position
from   app.api.v1 import explore        # Route combinee (theorie/moteur)
from   app.api.v1 import vector_search  # Route de recherche vectorielle (RAG)
from   app.api.v1 import agent          # Route de l'agent complet (LangGraph)
from   app.api.v1 import agent_llm      # Route de l'agent, variante LLM
from   app.api.v1 import videos         # Route de recherche de videos (YouTube)
from   app.core.dependances import obtenir_adaptateur_milvus    # Prechauffage
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="main")


# ##############################################################################
# Prechauffage : charge le modele d'embeddings AU DEMARRAGE, pas a la
# premiere requete utilisateur -- evite que le premier appel a
# /vector-search, /agent/invoke ou /agent-llm/invoke paye ce cout.
# ##############################################################################
@asynccontextmanager
async def cycle_de_vie(app: FastAPI):
    log.START_ACTION("main", "prechauffage", "Chargement du modele d'embeddings")
    debut = time.perf_counter()

    obtenir_adaptateur_milvus()    # Meme fabrique @lru_cache que les endpoints

    duree = time.perf_counter() - debut
    log.FINISH_ACTION(
        "main", "prechauffage", f"Modele charge en {duree:.1f}s -- pret",
    )
    yield
    # Rien a nettoyer a l'arret pour le moment.


# ##############################################################################
# Creation de l'application
# ##############################################################################
application = FastAPI(
    title       = "FFE Chess Agent API",
    description = "API de l'agent IA d'apprentissage des ouvertures",
    version     = "0.1.0",
    lifespan    = cycle_de_vie,
)

# Enregistrement des routeurs versionnes de l'API
application.include_router(healthcheck.routeur,   prefix="/api/v1")
application.include_router(moves.routeur,         prefix="/api/v1")
application.include_router(evaluate.routeur,      prefix="/api/v1")
application.include_router(explore.routeur,       prefix="/api/v1")
application.include_router(vector_search.routeur, prefix="/api/v1")
application.include_router(agent.routeur,         prefix="/api/v1")
application.include_router(agent_llm.routeur,     prefix="/api/v1")
application.include_router(videos.routeur,        prefix="/api/v1")

# ######################################################################
# GET / : racine de l'API, simple message de bienvenue
# ######################################################################
@application.get("/")
def racine() -> dict:
    """Confirme que le service repond, meme sans prefixe /api/v1."""
    return {"message": "Agent IA echecs FFE - backend operationnel"}
