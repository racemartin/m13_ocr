# ############################################################################
# Configuration partagee des tests (fixtures pytest)
# ############################################################################

# Bibliotheques tierces
import pytest    # Framework de test
from   fastapi.testclient import TestClient    # Client HTTP de test

# Modules internes
from   app.main import application    # Application FastAPI a tester

# Position de depart standard (utile pour la plupart des tests)
FEN_POSITION_DEPART = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
)
FEN_INVALIDE = "ceci-nest-pas-un-fen-valide"


@pytest.fixture
def client() -> TestClient:
    """Client de test HTTP branche sur l'application FastAPI."""
    return TestClient(application)


@pytest.fixture(autouse=True)
def nettoyer_surcharges_dependances():
    """Nettoie les dependency_overrides apres chaque test.

    Evite qu'une surcharge posee dans un test (fake adaptateur) ne
    "fuite" vers le test suivant.
    """
    yield
    application.dependency_overrides.clear()
