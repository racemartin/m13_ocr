# ############################################################################
# Adaptateur d'infrastructure : validation via python-chess
# ############################################################################
# Seul module du systeme qui importe la bibliotheque "chess". Implemente le
# port PortValidateurEchecs defini par le domaine.
#
# NOTE : ce module est appele a chaque requete (validation systematique du
# FEN entrant), donc les traces de succes restent en DEBUG pour ne pas
# noyer les logs de production ; seul le rejet d'un FEN invalide remonte
# en WARNING.

# Bibliotheques tierces
import chess    # Regles du jeu d'echecs (validation FEN, coups legaux)

# Modules internes
from   app.domaine.ports.port_validateur_echecs import (    # Port a
    PortValidateurEchecs,                                   # implementer
)
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="adaptateur_python_chess")


class AdaptateurPythonChess(PortValidateurEchecs):
    def valider_fen(self, fen: str) -> bool:
        try:
            chess.Board(fen)
        except ValueError:
            log.LEVEL_5_WARNING(
                "AdaptateurPythonChess", f"FEN invalide rejete : {fen}",
            )
            return False

        log.LEVEL_8_DEBUG("AdaptateurPythonChess", f"FEN valide : {fen}")
        return True

    def coups_legaux(self, fen: str) -> list[str]:
        plateau = chess.Board(fen)
        coups   = [coup.uci() for coup in plateau.legal_moves]

        log.LEVEL_8_DEBUG(
            "AdaptateurPythonChess",
            f"{len(coups)} coup(s) legal(aux) pour {fen}",
        )
        return coups
