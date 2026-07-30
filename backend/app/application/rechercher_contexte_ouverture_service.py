# ############################################################################
# Cas d'utilisation : rechercher du contexte sur une ouverture (RAG)
# ############################################################################
# Orchestre le port du domaine. Ne connait ni pymilvus, ni
# sentence-transformers : ceux-ci restent confines a l'adaptateur.

# Modules internes
from   app.domaine.modeles import ExtraitConnaissance          # Modele
from   app.domaine.ports.port_base_connaissances import (      # Port a
    PortBaseConnaissances,                                     # utiliser
)

TOP_K_PAR_DEFAUT = 3


class RechercherContexteOuvertureService:
    def __init__(self, base_connaissances: PortBaseConnaissances) -> None:
        self.base_connaissances = base_connaissances    # Port du domaine

    # ------------------------------------------------------------------
    # Execute le cas d'utilisation
    # ------------------------------------------------------------------
    def executer(
        self, requete: str, top_k: int = TOP_K_PAR_DEFAUT,
    ) -> list[ExtraitConnaissance]:
        """Retourne les extraits de contexte les plus pertinents.

        Une liste vide est une reponse valide : elle signifie qu'aucun
        contexte pertinent n'a ete trouve pour cette requete.
        """
        if not requete or not requete.strip():
            raise ValueError("La requete ne peut pas etre vide")

        return self.base_connaissances.rechercher_contexte(requete, top_k)
