"""Point d'entree de l'API FastAPI - Agent IA echecs (FFE).

Etape 1 de la mission : service "Hello World" minimal expose via
Docker Compose, avec une route de sante permettant de valider que le
conteneur fonctionne. Les routes metier (agent, Stockfish, Lichess,
Milvus, YouTube) seront ajoutees aux etapes suivantes.
"""

# ----------------------------------------------------------------
# Framework web principal de l'API
# ----------------------------------------------------------------
from fastapi import FastAPI  # creation de l'application ASGI

from app.api.v1 import healthcheck  # routes de verification sante
from app.core.config import parametres  # configuration centralisee

application = FastAPI(
    title   = parametres.nom_application,
    version = parametres.version_api,
)

# Enregistrement des routes de l'etape 1, prefixees par /api/v1
application.include_router(healthcheck.routeur, prefix="/api/v1")


# ######################################################################
# GET / : racine de l'API, simple message de bienvenue
# ######################################################################
@application.get("/")
def racine() -> dict:
    """Confirme que le service repond, meme sans prefixe /api/v1."""
    return {"message": "Agent IA echecs FFE - backend operationnel"}
