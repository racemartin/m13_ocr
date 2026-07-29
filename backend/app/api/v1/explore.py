# ############################################################################
# Route : exploration combinee d'une position (theorie, sinon evaluation)
# ############################################################################
# Traduit la requete HTTP vers ExplorerPositionService. Reproduit le flux
# demande par la FFE en une seule requete : coups theoriques (Lichess ->
# Polyglot) si connus, sinon evaluation Stockfish.

# Bibliotheques tierces
from   fastapi import APIRouter, Depends, HTTPException    # Framework web

# Modules internes
from   app.application.explorer_position_service import (   # Cas
    ExplorerPositionService,                                # d'usage
)
from   app.api.v1.schemas import (                          # Schemas HTTP
    ExplorationTheorieSchema, ExplorationEvaluationSchema,
    resultat_exploration_vers_schema,
)
from   app.core.dependances import obtenir_service_exploration  # Injection

routeur = APIRouter()

ReponseExploration = ExplorationTheorieSchema | ExplorationEvaluationSchema


# ############################################################################
# Endpoint : exploration combinee
# ############################################################################
# NOTE : {fen:path} (et non {fen}) car un FEN contient des "/" (separateurs
# de rangees) qui casseraient le routing standard de FastAPI sinon.
@routeur.get("/explore/{fen:path}", response_model=ReponseExploration)
def explorer_position(
    fen     : str,
    service : ExplorerPositionService = Depends(obtenir_service_exploration),
) -> ReponseExploration:
    """Retourne les coups theoriques connus, sinon une evaluation Stockfish.

    Le champ "type" du corps de reponse ("theorie" | "evaluation")
    indique quelle branche a repondu, pour que le client n'ait pas a
    deviner la forme des donnees.
    """
    try:
        resultat = service.executer(fen)
    except ValueError as erreur:
        raise HTTPException(status_code=422, detail=str(erreur)) from erreur

    return resultat_exploration_vers_schema(fen, resultat)
