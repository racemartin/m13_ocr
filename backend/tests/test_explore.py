# ############################################################################
# Tests : endpoint /api/v1/explore/{fen}
# ############################################################################
# Reutilise les memes fakes que test_moves.py / test_evaluate.py, composes
# a travers les deux services d'application existants.

# Modules internes
from   app.application.obtenir_coups_theoriques_service import (  # Cas
    ObtenirCoupsTheoriquesService,                                 # d'usage
)
from   app.application.evaluer_position_service import (    # Cas
    EvaluerPositionService,                                 # d'usage
)
from   app.application.explorer_position_service import (   # Cas
    ExplorerPositionService,                                # d'usage combine
)
from   app.core.dependances import obtenir_service_exploration  # Cablage
from   app.domaine.modeles import CoupTheorique, Evaluation   # Modeles
from   tests.conftest import FEN_POSITION_DEPART, FEN_INVALIDE
from   tests.fakes import (
    FauxValidateurEchecs, FauxTheorieOuvertures, FauxMoteurEvaluation,
)


def construire_service(coups=None, evaluation=None, fen_valide=True):
    service_coups = ObtenirCoupsTheoriquesService(
        validateur = FauxValidateurEchecs(fen_valide=fen_valide),
        theorie    = FauxTheorieOuvertures(coups=coups or []),
    )
    service_evaluation = EvaluerPositionService(
        validateur = FauxValidateurEchecs(fen_valide=fen_valide),
        moteur     = FauxMoteurEvaluation(evaluation=evaluation),
    )
    return ExplorerPositionService(
        service_coups      = service_coups,
        service_evaluation = service_evaluation,
    )


def test_explore_retourne_la_theorie_quand_elle_existe(client):
    coups = [CoupTheorique(uci="e2e4", san="e4", nombre_parties=125_000)]
    service = construire_service(coups=coups)
    client.app.dependency_overrides[obtenir_service_exploration] = (
        lambda: service
    )

    reponse = client.get(f"/api/v1/explore/{FEN_POSITION_DEPART}")

    assert reponse.status_code == 200
    assert reponse.json() == {
        "fen"  : FEN_POSITION_DEPART,
        "type" : "theorie",
        "coups": [{"uci": "e2e4", "san": "e4", "nombre_parties": 125_000}],
    }


def test_explore_retombe_sur_stockfish_si_aucune_theorie(client):
    evaluation = Evaluation(
        type="cp", valeur=39, coup_recommande="e2e4", profondeur=15,
    )
    service = construire_service(coups=[], evaluation=evaluation)
    client.app.dependency_overrides[obtenir_service_exploration] = (
        lambda: service
    )

    reponse = client.get(f"/api/v1/explore/{FEN_POSITION_DEPART}")

    assert reponse.status_code == 200
    assert reponse.json() == {
        "fen"       : FEN_POSITION_DEPART,
        "type"      : "evaluation",
        "evaluation": {"type": "cp", "value": 39, "score": "+0.39"},
        "best_move" : "e2e4",
        "depth"     : 15,
    }


def test_explore_fen_invalide_retourne_422(client):
    service = construire_service(fen_valide=False)
    client.app.dependency_overrides[obtenir_service_exploration] = (
        lambda: service
    )

    reponse = client.get(f"/api/v1/explore/{FEN_INVALIDE}")

    assert reponse.status_code == 422
