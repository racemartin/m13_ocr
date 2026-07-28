# ############################################################################
# Route : evaluation d'une position par Stockfish
# ############################################################################
# Traduit la requete HTTP vers le cas d'utilisation EvaluerPositionService,
# puis serialise le resultat. Ne connait ni python-chess, ni stockfish.

# Bibliotheques tierces
from   fastapi import APIRouter, Depends, HTTPException    # Framework web

# Modules internes
from   app.application.evaluer_position_service import (    # Cas
    EvaluerPositionService,                                  # d'usage
)
from   app.api.v1.schemas import EvaluationSchema           # Schema HTTP
from   app.core.dependances import obtenir_service_evaluation  # Injection

router = APIRouter()


# ############################################################################
# Endpoint : evaluation de position
# ############################################################################
# NOTE : {fen:path} (et non {fen}) car un FEN contient des "/" (separateurs
# de rangees) qui casseraient le routing standard de FastAPI sinon.
@router.get("/evaluate/{fen:path}", response_model=EvaluationSchema)
def evaluer_position(
    fen     : str,
    service : EvaluerPositionService = Depends(obtenir_service_evaluation),
) -> EvaluationSchema:
    """Retourne l'evaluation Stockfish (en centipawns ou mat) de `fen`."""
    try:
        evaluation = service.executer(fen)
    except ValueError as erreur:
        raise HTTPException(status_code=422, detail=str(erreur)) from erreur

    return EvaluationSchema.depuis_domaine(evaluation)
