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
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="adaptateur_stockfish")

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
            log.LEVEL_7_INFO(
                "AdaptateurStockfish",
                f"Demarrage du sous-processus Stockfish "
                f"(binaire={self.chemin_binaire}, "
                f"profondeur={self.profondeur})",
            )
            self._moteur = Stockfish(
                path  = self.chemin_binaire,
                depth = self.profondeur,
            )
        return self._moteur

    # ------------------------------------------------------------------
    # Evaluation de la position
    # ------------------------------------------------------------------
    def evaluer(self, fen: str) -> Evaluation:
        log.START_ACTION(
            "AdaptateurStockfish", "evaluer", "Evaluation de la position",
        )
        log.PARAMETER_VALUE("fen", fen)
        log.PARAMETER_VALUE("profondeur", self.profondeur)

        self.moteur.set_fen_position(fen)
        resultat      = self.moteur.get_evaluation()
        meilleur_coup = self.moteur.get_best_move()
        evaluation    = Evaluation(
            type            = resultat["type"],
            valeur          = resultat["value"],
            coup_recommande = meilleur_coup,
            profondeur      = self.profondeur,
        )

        log.PARAMETER_VALUE("type", evaluation.type)
        log.PARAMETER_VALUE("valeur", evaluation.valeur)
        log.PARAMETER_VALUE("coup_recommande", evaluation.coup_recommande)
        log.FINISH_ACTION(
            "AdaptateurStockfish", "evaluer",
            f"{evaluation.type}={evaluation.valeur} "
            f"coup={evaluation.coup_recommande}",
        )
        return evaluation
