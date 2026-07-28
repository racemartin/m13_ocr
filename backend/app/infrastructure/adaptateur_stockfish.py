# ############################################################################
# Adaptateur d'infrastructure : evaluation via le moteur Stockfish
# ############################################################################
# Seul module du systeme qui connait le binaire Stockfish et le paquet
# Python "stockfish". Implemente le port PortMoteurEvaluation du domaine.
#
# Le moteur est initialise de maniere paresseuse (lazy) : le sous-processus
# Stockfish n'est lance qu'au premier appel a evaluer(), et reutilise
# ensuite pour toutes les requetes suivantes (cout d'instanciation evite).

# Bibliotheques tierces
from   stockfish import Stockfish    # Wrapper du moteur d'echecs

# Modules internes
from   app.domaine.modeles import Evaluation                # Modele
from   app.domaine.ports.port_moteur_evaluation import (    # Port a
    PortMoteurEvaluation,                                   # implementer
)

# Profondeur de recherche par defaut du moteur
PROFONDEUR_PAR_DEFAUT = 15


class AdaptateurStockfish(PortMoteurEvaluation):
    def __init__(
        self,
        chemin_binaire : str,
        profondeur     : int = PROFONDEUR_PAR_DEFAUT,
    ) -> None:
        self.chemin_binaire = chemin_binaire
        self.profondeur     = profondeur
        self._moteur: Stockfish | None = None    # Instancie a la demande

    # ------------------------------------------------------------------
    # Initialisation paresseuse du sous-processus moteur
    # ------------------------------------------------------------------
    @property
    def moteur(self) -> Stockfish:
        if self._moteur is None:
            self._moteur = Stockfish(
                path  = self.chemin_binaire,
                depth = self.profondeur,
            )
        return self._moteur

    # ------------------------------------------------------------------
    # Evaluation de la position
    # ------------------------------------------------------------------
    def evaluer(self, fen: str) -> Evaluation:
        self.moteur.set_fen_position(fen)
        resultat = self.moteur.get_evaluation()
        return Evaluation(type=resultat["type"], valeur=resultat["value"])
