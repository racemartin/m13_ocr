# ############################################################################
# Port : validation d'une position d'echecs
# ############################################################################
# Contrat que doit respecter tout adaptateur charge de valider un FEN et
# d'en deduire les coups legaux. Le domaine ignore volontairement comment
# cette validation est realisee (python-chess ou toute autre implementation).

# Bibliotheque standard
from   abc import ABC, abstractmethod    # Classes abstraites


class PortValidateurEchecs(ABC):
    """Contrat de validation d'une position et de ses coups legaux."""

    @abstractmethod
    def valider_fen(self, fen: str) -> bool:
        """Indique si la chaine FEN represente une position valide."""
        ...

    @abstractmethod
    def coups_legaux(self, fen: str) -> list[str]:
        """Retourne les coups legaux depuis la position, en notation UCI."""
        ...
