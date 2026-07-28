# ############################################################################
# Cas d'utilisation : obtenir les coups theoriques d'une position
# ############################################################################
# Orchestre les ports du domaine. Ne connait ni python-chess, ni httpx, ni
# aucun detail d'implementation des adaptateurs : ceux-ci sont injectes.

# Modules internes
from   app.domaine.modeles import CoupTheorique                # Modele
from   app.domaine.ports.port_validateur_echecs import (       # Port
    PortValidateurEchecs,
)
from   app.domaine.ports.port_theorie_ouvertures import (      # Port
    PortTheorieOuvertures,
)


class ObtenirCoupsTheoriquesService:
    def __init__(
        self,
        validateur : PortValidateurEchecs,
        theorie    : PortTheorieOuvertures,
    ) -> None:
        self.validateur = validateur    # Port du domaine
        self.theorie    = theorie       # Port du domaine

    # ------------------------------------------------------------------
    # Execute le cas d'utilisation
    # ------------------------------------------------------------------
    def executer(self, fen: str) -> list[CoupTheorique]:
        """Retourne les coups theoriques connus depuis la position `fen`.

        Leve ValueError si le FEN fourni n'est pas une position valide.
        """
        if not self.validateur.valider_fen(fen):
            raise ValueError(f"FEN invalide : {fen}")

        return self.theorie.coups_theoriques(fen)
