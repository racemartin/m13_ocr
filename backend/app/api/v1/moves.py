# ############################################################################
# Route : coups theoriques d'une position (theorie des ouvertures)
# ############################################################################
# Traduit la requete HTTP vers le cas d'utilisation ObtenirCoupsTheoriques
# Service, puis serialise le resultat. Ne connait ni python-chess, ni httpx.

# Bibliotheques tierces
from   fastapi import APIRouter, Depends, HTTPException    # Framework web

# Modules internes
from   app.application.obtenir_coups_theoriques_service import (  # Cas
    ObtenirCoupsTheoriquesService,                                 # d'usage
)
from   app.api.v1.schemas import CoupTheoriqueSchema        # Schema HTTP
from   app.core.dependances import (                        # Injection
    obtenir_service_coups_theoriques,                        # de dependance
)

router = APIRouter()


# ############################################################################
# Endpoint : coups theoriques
# ############################################################################
# NOTE : {fen:path} (et non {fen}) car un FEN contient des "/" (separateurs
# de rangees) qui casseraient le routing standard de FastAPI sinon.
@router.get("/moves/{fen:path}", response_model=list[CoupTheoriqueSchema])
def obtenir_coups_theoriques(
    fen     : str,
    service : ObtenirCoupsTheoriquesService = Depends(
        obtenir_service_coups_theoriques,
    ),
) -> list[CoupTheoriqueSchema]:
    """Retourne les coups theoriques connus par Lichess depuis `fen`.

    Une liste vide est une reponse valide : elle signifie que la position
    est sortie de la theorie connue, pas qu'une erreur s'est produite.
    """
    try:
        coups = service.executer(fen)
    except ValueError as erreur:
        raise HTTPException(status_code=422, detail=str(erreur)) from erreur

    return [CoupTheoriqueSchema.depuis_domaine(coup) for coup in coups]
