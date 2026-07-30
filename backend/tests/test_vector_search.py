# ############################################################################
# Tests : endpoint /api/v1/vector-search
# ############################################################################
# Le fake remplace Milvus + sentence-transformers : ces tests ne
# necessitent aucun serveur Milvus ni telechargement de modele.

# Modules internes
from   app.application.rechercher_contexte_ouverture_service import (  # Cas
    RechercherContexteOuvertureService,                                 # d'usage
)
from   app.core.dependances import obtenir_service_recherche_contexte
from   app.domaine.modeles import ExtraitConnaissance
from   tests.fakes import FauxBaseConnaissances


def test_vector_search_retourne_les_extraits_pertinents(client):
    extraits = [
        ExtraitConnaissance(
            texte="La défense sicilienne est une ouverture...",
            ouverture="Défense sicilienne",
            source_url="https://fr.wikipedia.org/wiki/Défense_sicilienne",
            score=0.87,
        ),
    ]
    service = RechercherContexteOuvertureService(
        base_connaissances=FauxBaseConnaissances(extraits=extraits),
    )
    client.app.dependency_overrides[obtenir_service_recherche_contexte] = (
        lambda: service
    )

    reponse = client.get("/api/v1/vector-search", params={"q": "sicilienne"})

    assert reponse.status_code == 200
    assert reponse.json() == [{
        "texte"      : "La défense sicilienne est une ouverture...",
        "ouverture"  : "Défense sicilienne",
        "source_url" : "https://fr.wikipedia.org/wiki/Défense_sicilienne",
        "score"      : 0.87,
    }]


def test_vector_search_liste_vide_est_une_reponse_valide(client):
    service = RechercherContexteOuvertureService(
        base_connaissances=FauxBaseConnaissances(extraits=[]),
    )
    client.app.dependency_overrides[obtenir_service_recherche_contexte] = (
        lambda: service
    )

    reponse = client.get("/api/v1/vector-search", params={"q": "xyzabc"})

    assert reponse.status_code == 200
    assert reponse.json() == []


def test_vector_search_respecte_top_k(client):
    extraits = [
        ExtraitConnaissance(texte=f"Extrait {i}", ouverture="X",
                             source_url="https://x", score=1.0 - i * 0.1)
        for i in range(5)
    ]
    service = RechercherContexteOuvertureService(
        base_connaissances=FauxBaseConnaissances(extraits=extraits),
    )
    client.app.dependency_overrides[obtenir_service_recherche_contexte] = (
        lambda: service
    )

    reponse = client.get(
        "/api/v1/vector-search", params={"q": "test", "top_k": 2},
    )

    assert reponse.status_code == 200
    assert len(reponse.json()) == 2


def test_vector_search_sans_parametre_q_retourne_422(client):
    service = RechercherContexteOuvertureService(
        base_connaissances=FauxBaseConnaissances(),
    )
    client.app.dependency_overrides[obtenir_service_recherche_contexte] = (
        lambda: service
    )

    reponse = client.get("/api/v1/vector-search")

    assert reponse.status_code == 422
