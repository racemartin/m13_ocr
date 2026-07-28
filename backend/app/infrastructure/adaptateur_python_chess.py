# ############################################################################
# Adaptateur d'infrastructure : validation via python-chess
# ############################################################################
# Seul module du systeme qui importe la bibliotheque "chess". Implemente le
# port PortValidateurEchecs defini par le domaine.

# Bibliotheques tierces
import chess    # Regles du jeu d'echecs (validation FEN, coups legaux)

# Modules internes
from   app.domaine.ports.port_validateur_echecs import (    # Port a
    PortValidateurEchecs,                                   # implementer
)


class AdaptateurPythonChess(PortValidateurEchecs):
    def valider_fen(self, fen: str) -> bool:
        try:
            chess.Board(fen)
        except ValueError:
            return False
        return True

    def coups_legaux(self, fen: str) -> list[str]:
        plateau = chess.Board(fen)
        return [coup.uci() for coup in plateau.legal_moves]
