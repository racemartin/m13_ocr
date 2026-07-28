# ############################################################################
# Cas d'utilisation : evaluer une position avec le moteur d'echecs
# ############################################################################
# Orchestre les ports du domaine. Ne connait ni python-chess, ni stockfish,
# ni aucun detail d'implementation des adaptateurs : ceux-ci sont injectes.

# Modules internes
from   app.domaine.modeles import Evaluation                   # Modele
from   app.domaine.ports.port_validateur_echecs import (       # Port
    PortValidateurEchecs,
)
from   app.domaine.ports.port_moteur_evaluation import (       # Port
    PortMoteurEvaluation,
)


class EvaluerPositionService:
    def __init__(
        self,
        validateur : PortValidateurEchecs,
        moteur     : PortMoteurEvaluation,
    ) -> None:
        self.validateur = validateur    # Port du domaine
        self.moteur     = moteur        # Port du domaine

    # ------------------------------------------------------------------
    # Execute le cas d'utilisation
    # ------------------------------------------------------------------
    def executer(self, fen: str) -> Evaluation:
        """Retourne l'evaluation Stockfish de la position `fen`.

        Leve ValueError si le FEN fourni n'est pas une position valide.
        """
        if not self.validateur.valider_fen(fen):
            raise ValueError(f"FEN invalide : {fen}")

        return self.moteur.evaluer(fen)
