# ############################################################################
# Tests : endpoint /api/v1/evaluate/{fen}
# ############################################################################
# Les adaptateurs reels (python-chess, Stockfish) sont remplaces par des
# fakes via dependency_overrides : ces tests ne necessitent aucun binaire
# Stockfish installe sur la machine qui les execute.

# Modules internes
from   app.application.evaluer_position_service import (    # Cas
    EvaluerPositionService,                                  # d'usage
)
from   app.core.dependances import obtenir_service_evaluation  # Cablage
from   app.domaine.modeles import Evaluation                 # Modele
from   tests.conftest import FEN_POSITION_DEPART, FEN_INVALIDE
from   tests.fakes import FauxValidateurEchecs, FauxMoteurEvaluation


def test_evaluation_retourne_le_score_en_centipawns(client):
    service = EvaluerPositionService(
        validateur = FauxValidateurEchecs(fen_valide=True),
        moteur     = FauxMoteurEvaluation(
            evaluation=Evaluation(
                type="cp", valeur=35,
                coup_recommande="f1b5", profondeur=15,
            ),
        ),
    )
    client.app.dependency_overrides[obtenir_service_evaluation] = (
        lambda: service
    )

    reponse = client.get(f"/api/v1/evaluate/{FEN_POSITION_DEPART}")

    assert reponse.status_code == 200
    assert reponse.json() == {
        "fen"             : FEN_POSITION_DEPART,
        "evaluation"      : {"type": "cp", "valeur": 35, "score": "+0.35"},
        "coup_recommande" : "f1b5",
        "profondeur"      : 15,
    }


def test_evaluation_retourne_un_mat_annonce(client):
    service = EvaluerPositionService(
        validateur = FauxValidateurEchecs(fen_valide=True),
        moteur     = FauxMoteurEvaluation(
            evaluation=Evaluation(
                type="mate", valeur=3,
                coup_recommande="d1h5", profondeur=15,
            ),
        ),
    )
    client.app.dependency_overrides[obtenir_service_evaluation] = (
        lambda: service
    )

    reponse = client.get(f"/api/v1/evaluate/{FEN_POSITION_DEPART}")

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["evaluation"] == {"type": "mate", "valeur": 3, "score": "+#3"}
    assert corps["coup_recommande"] == "d1h5"


def test_evaluation_fen_invalide_retourne_422(client):
    service = EvaluerPositionService(
        validateur = FauxValidateurEchecs(fen_valide=False),
        moteur     = FauxMoteurEvaluation(),
    )
    client.app.dependency_overrides[obtenir_service_evaluation] = (
        lambda: service
    )

    reponse = client.get(f"/api/v1/evaluate/{FEN_INVALIDE}")

    assert reponse.status_code == 422
