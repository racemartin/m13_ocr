# ############################################################################
# Tests : endpoint /api/v1/healthcheck
# ############################################################################

# Modules internes
from   app.core.config import parametres    # Parametres reels de l'app

def test_healthcheck_repond_200_et_statut_ok(client):
    reponse = client.get("/api/v1/healthcheck")
 
    assert reponse.status_code == 200
 
    corps = reponse.json()
    assert corps["status"]      == "ok"
    assert corps["application"] == parametres.nom_application
    assert corps["version"]     == parametres.version_api
 