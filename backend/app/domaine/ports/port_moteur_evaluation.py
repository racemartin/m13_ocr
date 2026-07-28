# ############################################################################
# Port : moteur d'evaluation de position
# ############################################################################
# Contrat que doit respecter tout adaptateur charge d'evaluer une position.
# Le domaine ignore que cette evaluation provient de Stockfish : seul
# l'adaptateur infrastructure le sait.

# Bibliotheque standard
from   abc import ABC, abstractmethod    # Classes abstraites

# Modules internes
from   app.domaine.modeles import Evaluation    # Modele de domaine


class PortMoteurEvaluation(ABC):
    """Contrat d'evaluation d'une position par un moteur d'echecs."""

    @abstractmethod
    def evaluer(self, fen: str) -> Evaluation:
        """Retourne l'evaluation du moteur pour la position donnee."""
        ...
