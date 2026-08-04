# ############################################################################
# Port : recherche de videos explicatives (YouTube)
# ############################################################################
# Contrat que doit respecter tout adaptateur charge de rechercher des
# videos pertinentes pour une ouverture donnee. Le domaine ignore
# volontairement qu'il s'agit de YouTube : seul l'adaptateur infrastructure
# le sait.

# Bibliotheque standard
from   abc import ABC, abstractmethod    # Classes abstraites

# Modules internes
from   app.domaine.modeles import VideoExplicative    # Modele de domaine


class PortRechercheVideos(ABC):
    """Contrat de recherche de videos explicatives pertinentes."""

    @abstractmethod
    def rechercher(
        self, requete: str, max_resultats: int = 5,
    ) -> list[VideoExplicative]:
        """Retourne les videos les plus pertinentes pour la requete.

        Une liste vide signifie qu'aucune video pertinente n'a ete
        trouvee, pas necessairement une erreur technique (ex. quota
        API epuise doit etre gere par l'adaptateur, pas remonte tel quel).
        """
        ...
