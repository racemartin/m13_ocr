# ############################################################################
# Route : recherche vectorielle de contexte sur une ouverture (RAG)
# ############################################################################
# Traduit la requete HTTP vers RechercherContexteOuvertureService. Ne
# connait ni pymilvus, ni sentence-transformers.

# Bibliotheques tierces
from   fastapi import APIRouter, Depends, HTTPException, Query  # Framework

# Modules internes
from   app.application.rechercher_contexte_ouverture_service import (  # Cas
    RechercherContexteOuvertureService,                                 # d'usage
)
from   app.api.v1.schemas import ExtraitConnaissanceSchema  # Schema HTTP
from   app.core.dependances import (                        # Injection
    obtenir_service_recherche_contexte,
)

routeur = APIRouter()


# ############################################################################
# Endpoint : recherche vectorielle
# ############################################################################
@routeur.get(
    "/vector-search", response_model=list[ExtraitConnaissanceSchema],
)
def rechercher_contexte_ouverture(
    q       : str = Query(..., min_length=1, description="Requete ou nom d'ouverture"),
    top_k   : int = Query(3, ge=1, le=10, description="Nombre d'extraits a retourner"),
    service : RechercherContexteOuvertureService = Depends(
        obtenir_service_recherche_contexte,
    ),
) -> list[ExtraitConnaissanceSchema]:
    """Retourne les extraits de contexte les plus pertinents pour `q`.

    Une liste vide est une reponse valide : aucun contexte pertinent
    n'a ete trouve, ce n'est pas une erreur.
    """
    try:
        extraits = service.executer(q, top_k=top_k)
    except ValueError as erreur:
        raise HTTPException(status_code=422, detail=str(erreur)) from erreur

    return [ExtraitConnaissanceSchema.depuis_domaine(e) for e in extraits]
