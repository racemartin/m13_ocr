# ############################################################################
# Point d'entree pour LangGraph Studio -- grapheAvec doublures
# ############################################################################
# Expose le graphe reel (meme construire_graphe() que la production) mais
# compose avec des doublures des trois services, pour explorer la
# structure et faire des invocations d'exemple SANS toucher a MongoDB,
# Milvus ou Stockfish reels.
#
# Pour le graphe avec les VRAIS services (production), utiliser
# studio_graph_reel.py a la place dans langgraph.json.

# Bibliotheque standard
import sys
from pathlib import Path

# Rendre tests/fakes.py importable (memes doublures que la suite pytest)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tests"))

from app.application.obtenir_coups_theoriques_service import (
    ObtenirCoupsTheoriquesService,
)
from app.application.evaluer_position_service import EvaluerPositionService
from app.application.rechercher_contexte_ouverture_service import (
    RechercherContexteOuvertureService,
)
from app.application.agent.graphe_agent import construire_graphe

from app.domaine.modeles import CoupTheorique, Evaluation, ExtraitConnaissance

from fakes import (
    FauxValidateurEchecs, FauxTheorieOuvertures, FauxMoteurEvaluation,
    FauxBaseConnaissances,
)

# ----------------------------------------------------------------------
# Donnees de demonstration : une position AVEC theorie connue (branche
# "contexte" directe) -- modifie ici pour explorer l'autre branche
# (passe coups=[] pour forcer la branche "evaluer" -> Stockfish).
# ----------------------------------------------------------------------
service_coups = ObtenirCoupsTheoriquesService(
    validateur=FauxValidateurEchecs(),
    theorie=FauxTheorieOuvertures(coups=[
        CoupTheorique(uci="e2e4", san="e4", nombre_parties=125_000),
        CoupTheorique(uci="d2d4", san="d4", nombre_parties=98_000),
    ]),
)
service_evaluation = EvaluerPositionService(
    validateur=FauxValidateurEchecs(),
    moteur=FauxMoteurEvaluation(evaluation=Evaluation(
        type="cp", valeur=39, coup_recommande="e2e4", profondeur=15,
    )),
)
service_contexte = RechercherContexteOuvertureService(
    base_connaissances=FauxBaseConnaissances(extraits=[
        ExtraitConnaissance(
            texte="La partie italienne est l'une des plus anciennes ouvertures.",
            ouverture="Italienne",
            source_url="https://fr.wikipedia.org/wiki/Partie_italienne",
            score=0.87,
        ),
    ]),
)

# ----------------------------------------------------------------------
# def construire_graphe(
#     service_coups      : ObtenirCoupsTheoriquesService,
#     service_evaluation : EvaluerPositionService,
#     service_contexte   : RechercherContexteOuvertureService,
#     checkpointer       : BaseCheckpointSaver | None = None,
# ):
# ----------------------------------------------------------------------
    
graph = construire_graphe(
    service_coups, service_evaluation, service_contexte, checkpointer=None,
)
