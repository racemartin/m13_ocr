# ############################################################################
# Tests : endpoint /api/v1/moves/{fen}
# ############################################################################
# Les adaptateurs reels (python-chess, Lichess) sont remplaces par des
# fakes via dependency_overrides : ces tests ne font aucun appel reseau.

# Modules internes
from   app.application.obtenir_coups_theoriques_service import (  # Cas
    ObtenirCoupsTheoriquesService,                                 # d'usage
)
from   app.core.dependances import (                        # Point de
    obtenir_service_coups_theoriques,                        # cablage
)
from   app.domaine.modeles import CoupTheorique              # Modele
from   tests.conftest import FEN_POSITION_DEPART, FEN_INVALIDE
from   tests.fakes import FauxValidateurEchecs, FauxTheorieOuvertures


def test_coups_theoriques_retourne_les_coups_connus(client):
    coups_attendus = [
        CoupTheorique(uci="e2e4", san="e4", nombre_parties=125_000),
        CoupTheorique(uci="d2d4", san="d4", nombre_parties=98_000),
    ]
    service = ObtenirCoupsTheoriquesService(
        validateur = FauxValidateurEchecs(fen_valide=True),
        theorie    = FauxTheorieOuvertures(coups=coups_attendus),
    )
    client.app.dependency_overrides[obtenir_service_coups_theoriques] = (
        lambda: service
    )

    reponse = client.get(f"/api/v1/moves/{FEN_POSITION_DEPART}")

    assert reponse.status_code == 200
    assert reponse.json() == [
        {"uci": "e2e4", "san": "e4", "nombre_parties": 125_000},
        {"uci": "d2d4", "san": "d4", "nombre_parties": 98_000},
    ]


def test_coups_theoriques_liste_vide_est_une_reponse_valide(client):
    # Une position hors theorie doit repondre 200 avec une liste vide,
    # pas une erreur : c'est un resultat metier normal.
    service = ObtenirCoupsTheoriquesService(
        validateur = FauxValidateurEchecs(fen_valide=True),
        theorie    = FauxTheorieOuvertures(coups=[]),
    )
    client.app.dependency_overrides[obtenir_service_coups_theoriques] = (
        lambda: service
    )

    reponse = client.get(f"/api/v1/moves/{FEN_POSITION_DEPART}")

    assert reponse.status_code == 200
    assert reponse.json() == []


def test_coups_theoriques_fen_invalide_retourne_422(client):
    service = ObtenirCoupsTheoriquesService(
        validateur = FauxValidateurEchecs(fen_valide=False),
        theorie    = FauxTheorieOuvertures(),
    )
    client.app.dependency_overrides[obtenir_service_coups_theoriques] = (
        lambda: service
    )

    reponse = client.get(f"/api/v1/moves/{FEN_INVALIDE}")

    assert reponse.status_code == 422
