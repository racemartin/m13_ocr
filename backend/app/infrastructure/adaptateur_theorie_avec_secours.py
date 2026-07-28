# ############################################################################
# Adaptateur d'infrastructure : theorie des ouvertures avec repli local
# ############################################################################
# Compose deux adaptateurs implementant le meme port : tente d'abord la
# source principale (Lichess, plus riche mais dependante d'un service
# externe), puis retombe sur la source de secours (livre Polyglot local,
# toujours disponible) si la principale ne renvoie rien.
#
# Le domaine et l'application ne voient toujours qu'un seul
# PortTheorieOuvertures : ce cablage reste un detail d'infrastructure.
#
# C'est ici, et nulle part ailleurs, que l'on sait quelle source a
# reellement repondu : c'est donc le point de journalisation le plus
# important du trio Lichess / Polyglot / Stockfish.

# Modules internes
from   app.domaine.modeles import CoupTheorique                # Modele
from   app.domaine.ports.port_theorie_ouvertures import (      # Port a
    PortTheorieOuvertures,                                     # implementer
)
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="adaptateur_theorie_avec_secours")


class AdaptateurTheorieAvecSecours(PortTheorieOuvertures):
    def __init__(
        self,
        principal : PortTheorieOuvertures,
        secours   : PortTheorieOuvertures,
    ) -> None:
        self.principal = principal    # Ex. AdaptateurLichess
        self.secours   = secours      # Ex. AdaptateurPolyglot

    # ------------------------------------------------------------------
    # Tente la source principale, retombe sur le secours si necessaire
    # ------------------------------------------------------------------
    def coups_theoriques(self, fen: str) -> list[CoupTheorique]:
        log.START_ACTION(
            "AdaptateurTheorieAvecSecours", "coups_theoriques",
            "Choix de la source de theorie des ouvertures",
        )
        log.PARAMETER_VALUE("fen", fen)

        coups = self.principal.coups_theoriques(fen)

        if coups:
            log.PARAMETER_VALUE("source_utilisee", "principal (Lichess)")
            log.FINISH_ACTION(
                "AdaptateurTheorieAvecSecours", "coups_theoriques",
                f"Source principale : {len(coups)} coup(s)",
            )
            return coups

        log.LEVEL_6_NOTICE(
            "AdaptateurTheorieAvecSecours",
            f"Source principale vide/indisponible pour {fen}, "
            "utilisation du livre Polyglot de secours",
        )
        coups_secours = self.secours.coups_theoriques(fen)

        log.PARAMETER_VALUE("source_utilisee", "secours (Polyglot)")
        log.FINISH_ACTION(
            "AdaptateurTheorieAvecSecours", "coups_theoriques",
            f"Source de secours : {len(coups_secours)} coup(s)",
        )
        return coups_secours
