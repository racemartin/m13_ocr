# ############################################################################
# Port : identification du code ECO d'une position
# ############################################################################
# Contrat que doit respecter tout adaptateur charge d'identifier le code
# ECO (Encyclopedia of Chess Openings) d'une position donnee. Le domaine
# ignore volontairement la source des donnees (dataset Lichess, table
# maison, service tiers) : seul l'adaptateur infrastructure le sait.

# Bibliotheque standard
from   abc import ABC, abstractmethod    # Classes abstraites

# Modules internes
from   app.domaine.modeles import InfoEco    # Modele de domaine


class PortIdentificationEco(ABC):
    """Contrat d'identification ECO d'une position donnee par son FEN."""

    @abstractmethod
    def identifier(self, fen: str) -> InfoEco | None:
        """Retourne le code ECO et le nom de l'ouverture correspondant a
        cette position exacte, ou None si la position ne correspond a
        aucune ligne theorique cataloguee (position non standard, ou
        trop profonde pour figurer dans la base ECO)."""
        ...
