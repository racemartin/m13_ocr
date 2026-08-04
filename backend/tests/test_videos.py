# ############################################################################
# Tests : endpoint GET /api/v1/videos/{ouverture}
# ############################################################################
# Utilise FauxRechercheVideos : aucun appel reseau, aucune cle API
# consommee. Verifie le cas d'utilisation independamment du graphe agent.
# Le nettoyage des dependency_overrides est deja assure par la fixture
# autouse nettoyer_surcharges_dependances (conftest.py).

# Modules internes
from   app.main import application
from   app.core import dependances
from   app.domaine.modeles import VideoExplicative
from   app.application.rechercher_videos_service import (
    RechercherVideosService,
)
from   tests.fakes import FauxRechercheVideos


def test_rechercher_videos_retourne_les_resultats(client):
    videos = [
        VideoExplicative(
            id_video="abc123", titre="Sicilian Defense Explained",
            chaine="ChessCoach", url="https://www.youtube.com/watch?v=abc123",
        ),
    ]
    service_test = RechercherVideosService(
        recherche_videos=FauxRechercheVideos(videos=videos),
    )
    application.dependency_overrides[dependances.obtenir_service_videos] = (
        lambda: service_test
    )

    reponse = client.get("/api/v1/videos/Sicilienne")

    assert reponse.status_code == 200
    corps = reponse.json()
    assert len(corps) == 1
    assert corps[0]["id_video"] == "abc123"
    assert corps[0]["url"] == "https://www.youtube.com/watch?v=abc123"


def test_rechercher_videos_liste_vide_est_valide(client):
    service_test = RechercherVideosService(
        recherche_videos=FauxRechercheVideos(videos=[]),
    )
    application.dependency_overrides[dependances.obtenir_service_videos] = (
        lambda: service_test
    )

    reponse = client.get("/api/v1/videos/OuvertureInconnue")

    assert reponse.status_code == 200
    assert reponse.json() == []
