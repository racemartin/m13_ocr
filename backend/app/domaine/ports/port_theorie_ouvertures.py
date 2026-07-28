# ############################################################################
# Port : theorie des ouvertures
# ############################################################################
# Contrat que doit respecter tout adaptateur charge de fournir les coups
# theoriques connus depuis une position donnee. Le domaine ignore que cette
# donnee provient de l'API Lichess : seul l'adaptateur infrastructure le sait.

# Bibliotheque standard
from   abc import ABC, abstractmethod    # Classes abstraites

# Modules internes
from   app.domaine.modeles import CoupTheorique    # Modele de domaine


class PortTheorieOuvertures(ABC):
    """Contrat de recuperation des coups theoriques d'une position."""

    @abstractmethod
    def coups_theoriques(self, fen: str) -> list[CoupTheorique]:
        """Retourne les coups theoriques connus depuis la position.

        Une liste vide signifie qu'aucun coup theorique n'est connu (la
        position est sortie des sentiers battus), pas necessairement une
        erreur technique.
        """
        ...
