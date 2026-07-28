"""Point d'entree de l'API FastAPI - Agent IA echecs (FFE).

Etape 1 de la mission : service "Hello World" minimal expose via
Docker Compose, avec une route de sante permettant de valider que le
conteneur fonctionne. Les routes metier (agent, Stockfish, Lichess,
Milvus, YouTube) seront ajoutees aux etapes suivantes.
"""

# ############################################################################
# Point d'entree de l'application FastAPI
# ############################################################################
# Ce module cree l'instance FastAPI et enregistre les routeurs de l'API.
# La logique metier ne vit jamais ici : ce fichier est un adaptateur
# d'entree (driving adapter) qui expose la couche domaine via HTTP.


# ----------------------------------------------------------------
# Framework web principal de l'API
# ----------------------------------------------------------------
from fastapi import FastAPI  # creation de l'application ASGI

# Modules internes
from   app.api.v1 import healthcheck      # Route de verification de sante
from   app.api.v1 import moves            # Route des coups theoriques
from   app.api.v1 import evaluate         # Route d'evaluation de position
from   app.core.config import parametres  # configuration centralisee

application = FastAPI(
    title       = parametres.nom_application,
    description = "API de l'agent IA d'apprentissage des ouvertures",
    version     = parametres.version_api,
)

# Enregistrement des routes de l'etape 1, prefixees par /api/v1
application.include_router(healthcheck.routeur, prefix="/api/v1")
application.include_router(moves.router,       prefix="/api/v1")
application.include_router(evaluate.router,    prefix="/api/v1")

# ######################################################################
# GET / : racine de l'API, simple message de bienvenue
# ######################################################################
@application.get("/")
def racine() -> dict:
    """Confirme que le service repond, meme sans prefixe /api/v1."""
    return {"message": "Agent IA echecs FFE - backend operationnel"}
