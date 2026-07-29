# ############################################################################
# Cas d'utilisation : explorer une position (theorie, sinon evaluation)
# ############################################################################
# Compose deux cas d'utilisation deja existants (ObtenirCoupsTheoriques
# Service, EvaluerPositionService) pour reproduire le flux demande par la
# FFE : proposer d'abord les coups theoriques connus, et retomber sur une
# evaluation Stockfish uniquement si la position est sortie des sentiers
# battus (aucun coup theorique trouve, ni via Lichess ni via Polyglot).
#
# C'est ici, et nulle part ailleurs, que la decision "theorie ou moteur"
# est prise : le point de journalisation le plus important de ce flux.

# Modules internes
from   app.application.obtenir_coups_theoriques_service import (  # Cas
    ObtenirCoupsTheoriquesService,                                 # d'usage
)
from   app.application.evaluer_position_service import (    # Cas
    EvaluerPositionService,                                 # d'usage
)
from   app.domaine.modeles import ResultatExploration        # Modele
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="explorer_position_service")


class ExplorerPositionService:
    def __init__(
        self,
        service_coups      : ObtenirCoupsTheoriquesService,
        service_evaluation : EvaluerPositionService,
    ) -> None:
        self.service_coups      = service_coups
        self.service_evaluation = service_evaluation

    # ------------------------------------------------------------------
    # Theorie d'abord ; moteur seulement si aucun coup theorique connu
    # ------------------------------------------------------------------
    def executer(self, fen: str) -> ResultatExploration:
        log.START_ACTION(
            "ExplorerPositionService", "executer",
            "Exploration de la position (theorie puis, si besoin, moteur)",
        )
        log.PARAMETER_VALUE("fen", fen)

        # Leve ValueError si le FEN est invalide (propage tel quel au
        # routeur, qui la traduit en HTTP 422)
        coups = self.service_coups.executer(fen)

        if coups:
            log.PARAMETER_VALUE("type_resultat", "theorie")
            log.FINISH_ACTION(
                "ExplorerPositionService", "executer",
                f"Theorie : {len(coups)} coup(s)",
            )
            return ResultatExploration(type="theorie", coups=coups)

        log.LEVEL_6_NOTICE(
            "ExplorerPositionService",
            f"Aucun coup theorique pour {fen}, appel au moteur Stockfish",
        )
        evaluation = self.service_evaluation.executer(fen)

        log.PARAMETER_VALUE("type_resultat", "evaluation")
        log.FINISH_ACTION(
            "ExplorerPositionService", "executer",
            f"Evaluation : {evaluation.type}={evaluation.valeur}",
        )
        return ResultatExploration(type="evaluation", evaluation=evaluation)
