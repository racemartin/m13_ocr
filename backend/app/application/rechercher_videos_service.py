# ############################################################################
# Cas d'utilisation : rechercher des videos explicatives pour une ouverture
# ############################################################################
# Compose la requete de recherche "intelligente" demandee par la mission
# (nom de l'ouverture + mots-cles chess opening/tutorial/explanation) et
# delegue au port de recherche de videos. Aucune connaissance de YouTube
# ici -- uniquement la regle metier de construction de la requete.

# Modules internes
from   app.domaine.modeles import VideoExplicative
from   app.domaine.ports.port_recherche_videos import PortRechercheVideos
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="rechercher_videos_service")

MOTS_CLES_PAR_DEFAUT = "chess opening tutorial explanation"


class RechercherVideosService:
    def __init__(self, recherche_videos: PortRechercheVideos) -> None:
        self.recherche_videos = recherche_videos

    # ------------------------------------------------------------------
    # Construit une requete "intelligente" puis delegue au port
    # ------------------------------------------------------------------
    def executer(
        self, nom_ouverture: str, max_resultats: int = 3,
    ) -> list[VideoExplicative]:
        requete = f"{nom_ouverture} {MOTS_CLES_PAR_DEFAUT}"

        log.START_ACTION(
            "RechercherVideosService", "executer",
            f"Recherche de videos pour l'ouverture : {nom_ouverture}",
        )
        log.PARAMETER_VALUE("requete_construite", requete)

        videos = self.recherche_videos.rechercher(requete, max_resultats)

        if not videos:
            log.LEVEL_6_NOTICE(
                "RechercherVideosService",
                f"Aucune video pertinente pour '{nom_ouverture}' -- "
                "l'agent devra s'en passer pour cette reponse",
            )

        log.FINISH_ACTION(
            "RechercherVideosService", "executer",
            f"{len(videos)} video(s) retenue(s)",
        )
        return videos
