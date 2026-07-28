"""Route de verification que le conteneur backend fonctionne."""

# ----------------------------------------------------------------
# Framework web utilise pour exposer les routes de l'API
# ----------------------------------------------------------------
from fastapi import APIRouter  # creation d'un routeur independant

from app.core.config import parametres  # parametres de l'application

routeur = APIRouter()


# ######################################################################
# GET /api/v1/healthcheck : confirme que l'API repond correctement
# ######################################################################


@routeur.get("/healthcheck")
def healthcheck() -> dict:
    """Retourne un statut simple utilise pour valider le deploiement.

    Utilise en etape 1 pour verifier que le conteneur Docker du
    backend demarre et repond correctement, avant d'y brancher la
    logique metier (agent, Stockfish, Lichess, Milvus, YouTube).
    """
    return {
        "status"      : "ok",
        "application" : parametres.nom_application,
        "version"     : parametres.version_api,
    }
