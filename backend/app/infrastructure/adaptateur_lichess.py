# ############################################################################
# Adaptateur d'infrastructure : theorie des ouvertures via l'API Lichess
# ############################################################################
# Seul module du systeme qui connait l'URL et le format HTTP de l'Opening
# Explorer Lichess. Implemente le port PortTheorieOuvertures du domaine.

# Bibliotheques tierces
import httpx    # Client HTTP avec gestion de timeout

# Modules internes
from   app.domaine.modeles import CoupTheorique                # Modele
from   app.domaine.ports.port_theorie_ouvertures import (      # Port a
    PortTheorieOuvertures,                                     # implementer
)
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="adaptateur_lichess")

# Delai maximal accorde a l'API Lichess avant abandon de la requete
DELAI_TIMEOUT_SECONDES = 5.0


class AdaptateurLichess(PortTheorieOuvertures):
    def __init__(
        self,
        url_base : str = "https://explorer.lichess.ovh/masters",
        timeout  : float = DELAI_TIMEOUT_SECONDES,
    ) -> None:
        self.url_base = url_base
        self.timeout  = timeout

    # ------------------------------------------------------------------
    # Interrogation de l'API et conversion vers le modele de domaine
    # ------------------------------------------------------------------
    def coups_theoriques(self, fen: str) -> list[CoupTheorique]:
        log.START_ACTION(
            "AdaptateurLichess", "coups_theoriques",
            "Interrogation de l'API Lichess (Opening Explorer)",
        )
        log.PARAMETER_VALUE("fen", fen)
        log.PARAMETER_VALUE("url_base", self.url_base)

        try:
            reponse = httpx.get(
                self.url_base,
                params  = {"fen": fen},
                timeout = self.timeout,
            )
            reponse.raise_for_status()
        except httpx.TimeoutException:
            log.LEVEL_5_WARNING(
                "AdaptateurLichess", f"Timeout Lichess pour le FEN : {fen}",
            )
            log.FINISH_ACTION(
                "AdaptateurLichess", "coups_theoriques", "Timeout",
            )
            return []
        except httpx.HTTPError as erreur:
            log.LEVEL_5_WARNING(
                "AdaptateurLichess", f"Erreur HTTP Lichess : {erreur}",
            )
            log.FINISH_ACTION(
                "AdaptateurLichess", "coups_theoriques", "Erreur HTTP",
            )
            return []

        donnees = reponse.json()
        coups = [
            CoupTheorique(
                uci            = coup["uci"],
                san            = coup["san"],
                nombre_parties = coup.get("white", 0)
                                + coup.get("draws", 0)
                                + coup.get("black", 0),
            )
            for coup in donnees.get("moves", [])
        ]

        log.PARAMETER_VALUE("nombre_coups_trouves", len(coups))
        log.FINISH_ACTION(
            "AdaptateurLichess", "coups_theoriques",
            f"{len(coups)} coup(s) trouve(s)",
        )
        return coups
