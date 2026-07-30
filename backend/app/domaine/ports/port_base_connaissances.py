# ############################################################################
# Port : base de connaissances vectorielle (RAG)
# ############################################################################
# Contrat que doit respecter tout adaptateur charge d'indexer et de
# rechercher du contexte textuel par similarite vectorielle. Le domaine
# ignore volontairement qu'il s'agit de Milvus : seul l'adaptateur
# infrastructure le sait.

# Bibliotheque standard
from   abc import ABC, abstractmethod    # Classes abstraites

# Modules internes
from   app.domaine.modeles import ExtraitConnaissance    # Modele de domaine


class PortBaseConnaissances(ABC):
    """Contrat d'indexation et de recherche vectorielle de contexte."""

    @abstractmethod
    def indexer_documents(self, dossier: str) -> int:
        """Indexe tous les documents .md d'un dossier dans la base.

        Retourne le nombre de documents effectivement indexes.
        """
        ...

    @abstractmethod
    def rechercher_contexte(
        self, requete: str, top_k: int = 3,
    ) -> list[ExtraitConnaissance]:
        """Retourne les extraits les plus pertinents pour la requete.

        Une liste vide signifie qu'aucun contexte pertinent n'a ete
        trouve, pas necessairement une erreur technique.
        """
        ...
