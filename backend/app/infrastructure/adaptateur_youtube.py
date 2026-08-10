# ############################################################################
# Adaptateur d'infrastructure : recherche de videos (YouTube Data API v3)
# ############################################################################
# Seul module du systeme qui importe google-api-python-client. Traduit les
# erreurs specifiques a l'API (quota depasse, cle invalide) en un simple
# retour de liste vide, journalise : le domaine et l'application n'ont pas
# a savoir que la source est YouTube ni comment elle peut echouer.
#
# Deux appels API distincts, volontairement separes :
#   1. search().list()  -- trouve les videos candidates (cher : 100 unites)
#   2. videos().list()  -- recupere duree + nb de vues (peu cher : 1 unite)
# Le deuxieme appel est ce qui rend possible le filtre "qualite/pertinence"
# demande par la mission : search() seul ne renvoie ni l'un ni l'autre.

# Bibliotheque standard
import re                    # Parsing de la duree ISO 8601 (PT10M30S)
from   typing import Any    # Reponse brute de l'API (dict non type)

# Bibliotheques tierces
from   googleapiclient.discovery import build       # Client API Google
from   googleapiclient.errors import HttpError      # Erreurs HTTP de l'API

# Modules internes
from   app.domaine.modeles import VideoExplicative                  # Modele
from   app.domaine.ports.port_recherche_videos import (             # Port a
    PortRechercheVideos,                                            # implem.
)
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="adaptateur_youtube")

# ----------------------------------------------------------------------
# Seuils du filtre qualite/pertinence (point de vigilance de la mission)
# ----------------------------------------------------------------------
DUREE_MIN_SECONDES = 120     # < 2 min : quasi toujours un Short/extrait
DUREE_MAX_SECONDES = 2400    # > 40 min : peu credible comme explication
                              # ciblee d'une position/ouverture precise
VUES_MINIMUM        = 500    # Filtre grossier anti-spam/contenu abandonne

# Regex pour une duree ISO 8601 du type "PT1H2M10S" (heures/minutes/
# secondes optionnels, tous absents = 0)
_MOTIF_DUREE_ISO8601 = re.compile(
    r"PT(?:(?P<heures>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<secondes>\d+)S)?"
)


def _duree_en_secondes(duree_iso8601: str) -> int:
    """Convertit une duree ISO 8601 (ex. 'PT10M30S') en secondes."""
    m = _MOTIF_DUREE_ISO8601.match(duree_iso8601)
    if not m:
        return 0
    h  = int(m.group("heures")   or 0)
    mn = int(m.group("minutes")  or 0)
    s  = int(m.group("secondes") or 0)
    return h * 3600 + mn * 60 + s


class AdaptateurYoutube(PortRechercheVideos):
    def __init__(self, cle_api: str) -> None:
        self._client = build("youtube", "v3", developerKey=cle_api)

    # ------------------------------------------------------------------
    # Recherche de videos, avec gestion explicite du quota/des erreurs
    # ------------------------------------------------------------------
    def rechercher(
        self, requete: str, max_resultats: int = 5,
    ) -> list[VideoExplicative]:
        log.START_ACTION(
            "AdaptateurYoutube", "rechercher",
            "Recherche de videos explicatives sur YouTube",
        )
        log.PARAMETER_VALUE("requete", requete)

        try:
            reponse: dict[str, Any] = self._client.search().list(
                q           = requete,
                part        = "snippet",
                type        = "video",
                maxResults  = max_resultats,
                relevanceLanguage = "fr",
            ).execute()

        except HttpError as erreur:
            log.LEVEL_6_NOTICE(
                "AdaptateurYoutube",
                f"Echec API YouTube (quota ou cle invalide ?) : {erreur}",
            )
            log.FINISH_ACTION(
                "AdaptateurYoutube", "rechercher",
                "0 video (erreur API, voir notice ci-dessus)",
            )
            return []

        except Exception as erreur:
            log.LEVEL_6_NOTICE(
                "AdaptateurYoutube",
                f"Echec reseau vers l'API YouTube ({type(erreur).__name__}) : "
                f"{erreur}",
            )
            log.FINISH_ACTION(
                "AdaptateurYoutube", "rechercher",
                "0 video (echec reseau, voir notice ci-dessus)",
            )
            return []

        candidats = reponse.get("items", [])
        if not candidats:
            log.FINISH_ACTION(
                "AdaptateurYoutube", "rechercher", "0 video (aucun candidat)",
            )
            return []

        videos = self._enrichir_et_filtrer(candidats)

        log.FINISH_ACTION(
            "AdaptateurYoutube", "rechercher",
            f"{len(videos)} video(s) retenue(s) sur {len(candidats)} "
            "candidat(es) (apres filtre qualite)",
        )
        return videos

    # ------------------------------------------------------------------
    # Deuxieme appel API : duree + vues, puis filtre qualite/pertinence
    # ------------------------------------------------------------------
    def _enrichir_et_filtrer(
        self, candidats: list[dict[str, Any]],
    ) -> list[VideoExplicative]:
        ids = [item["id"]["videoId"] for item in candidats]

        try:
            details = self._client.videos().list(
                part = "contentDetails,statistics",
                id   = ",".join(ids),
            ).execute()

        except Exception as erreur:
            # ------------------------------------------------------------
            # Le filtre qualite est une amelioration, pas une dependance
            # dure : si CET appel-ci echoue (quota, reseau), on degrade
            # en douceur en renvoyant les resultats de recherche bruts
            # plutot que de perdre des videos par ailleurs valides.
            # ------------------------------------------------------------
            log.LEVEL_6_NOTICE(
                "AdaptateurYoutube",
                f"Echec de l'enrichissement qualite ({type(erreur).__name__}), "
                f"repli sur les resultats non filtres : {erreur}",
            )
            return [
                VideoExplicative(
                    id_video = item["id"]["videoId"],
                    titre    = item["snippet"]["title"],
                    chaine   = item["snippet"]["channelTitle"],
                    url      = f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                )
                for item in candidats
            ]

        infos_par_id = {item["id"]: item for item in details.get("items", [])}

        videos_retenues  = []
        nb_ecartes_duree = 0
        nb_ecartes_vues  = 0

        for item in candidats:
            id_video = item["id"]["videoId"]
            infos    = infos_par_id.get(id_video)
            if infos is None:
                continue    # Video supprimee/privee entre les deux appels

            duree_s = _duree_en_secondes(infos["contentDetails"]["duration"])
            vues    = int(infos["statistics"].get("viewCount", 0))

            if not (DUREE_MIN_SECONDES <= duree_s <= DUREE_MAX_SECONDES):
                nb_ecartes_duree += 1
                continue
            if vues < VUES_MINIMUM:
                nb_ecartes_vues += 1
                continue

            videos_retenues.append(VideoExplicative(
                id_video = id_video,
                titre    = item["snippet"]["title"],
                chaine   = item["snippet"]["channelTitle"],
                url      = f"https://www.youtube.com/watch?v={id_video}",
                vues     = vues,
            ))

        if nb_ecartes_duree or nb_ecartes_vues:
            log.LEVEL_6_NOTICE(
                "AdaptateurYoutube",
                f"Filtre qualite : {nb_ecartes_duree} ecartee(s) pour la "
                f"duree, {nb_ecartes_vues} ecartee(s) pour un nombre de "
                "vues insuffisant",
            )

        return videos_retenues