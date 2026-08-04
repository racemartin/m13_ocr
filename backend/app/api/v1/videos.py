# ############################################################################
# Route : recherche de videos explicatives pour une ouverture
# ############################################################################
# Traduit la requete HTTP vers RechercherVideosService. Endpoint totalement
# independant du graphe LangGraph : testable seul, avant tout cablage dans
# l'agent (cf. quickstart pour le tester directement avec curl/Insomnia).

# Bibliotheques tierces
from   fastapi import APIRouter, Depends    # Framework web
from   pydantic import BaseModel            # Schema de reponse

# Modules internes
from   app.application.rechercher_videos_service import (    # Cas
    RechercherVideosService,                                  # d'usage
)
from   app.core.dependances import obtenir_service_videos    # Injection

routeur = APIRouter()


class VideoSchema(BaseModel):
    id_video : str
    titre    : str
    chaine   : str
    url      : str
    vues     : int = 0


# ############################################################################
# Endpoint : videos explicatives pour une ouverture
# ############################################################################
@routeur.get("/videos/{ouverture}", response_model=list[VideoSchema])
def rechercher_videos(
    ouverture : str,
    service   : RechercherVideosService = Depends(obtenir_service_videos),
) -> list[VideoSchema]:
    """Retourne des videos YouTube pertinentes pour `ouverture`.

    Une liste vide est une reponse valide (pas d'erreur HTTP) : signifie
    qu'aucune video pertinente n'a ete trouvee pour cette recherche.
    """
    videos = service.executer(ouverture)

    return [
        VideoSchema(
            id_video = v.id_video, titre = v.titre,
            chaine   = v.chaine,   url   = v.url,
            vues     = v.vues,
        )
        for v in videos
    ]