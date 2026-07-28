# ############################################################################
# Adaptateur d'infrastructure : theorie des ouvertures via l'API Lichess
# ############################################################################
# Seul module du systeme qui connait l'URL et le format HTTP de l'Opening
# Explorer Lichess. Implemente le port PortTheorieOuvertures du domaine.

# Bibliotheque standard
import logging    # Journalisation des erreurs reseau

# Bibliotheques tierces
import httpx    # Client HTTP avec gestion de timeout

# Modules internes
from   app.domaine.modeles import CoupTheorique                # Modele
from   app.domaine.ports.port_theorie_ouvertures import (      # Port a
    PortTheorieOuvertures,                                     # implementer
)

journal = logging.getLogger(__name__)

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
        try:
            reponse = httpx.get(
                self.url_base,
                params  = {"fen": fen},
                timeout = self.timeout,
            )
            reponse.raise_for_status()
        except httpx.TimeoutException:
            journal.warning("Timeout Lichess pour le FEN : %s", fen)
            return []
        except httpx.HTTPError as erreur:
            journal.warning("Erreur HTTP Lichess : %s", erreur)
            return []

        donnees = reponse.json()
        return [
            CoupTheorique(
                uci            = coup["uci"],
                san            = coup["san"],
                nombre_parties = coup.get("white", 0)
                                + coup.get("draws", 0)
                                + coup.get("black", 0),
            )
            for coup in donnees.get("moves", [])
        ]
