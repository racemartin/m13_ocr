# ############################################################################
# Cablage des dependances (composition root)
# ############################################################################
# Seul module autorise a relier les ports du domaine a leurs adaptateurs
# concrets. Les routers FastAPI ne dependent que des fonctions ci-dessous
# via Depends(), jamais directement des classes d'infrastructure.

# Bibliotheque standard
import os                       # Lecture des variables d'environnement
from   pathlib import Path           # Construction robuste de chemins
from   functools import lru_cache    # Instances singleton reutilisables

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
from   app.infrastructure.adaptateur_python_chess import (  # Adaptateur
    AdaptateurPythonChess,
)
from   app.infrastructure.adaptateur_lichess import (       # Adaptateur
    AdaptateurLichess,
)
from   app.infrastructure.adaptateur_polyglot import (      # Adaptateur
    AdaptateurPolyglot,                                     # (secours local)
)
from   app.infrastructure.adaptateur_theorie_avec_secours import (  # Compo-
    AdaptateurTheorieAvecSecours,                                    # sition
)
from   app.infrastructure.adaptateur_stockfish import (     # Adaptateur
    AdaptateurStockfish,
)

# Chemin par defaut du binaire Stockfish dans l'image Docker (Debian/apt)
CHEMIN_STOCKFISH_PAR_DEFAUT = "/usr/games/stockfish"

# Chemin par defaut du livre Polyglot de secours (relatif a app/core/)
CHEMIN_LIVRE_POLYGLOT_PAR_DEFAUT = str(
    Path(__file__).resolve().parent.parent.parent
    / "data" / "polyglot" / "livre_ouvertures.bin"
)


# ------------------------------------------------------------------------
# Adaptateurs (une seule instance reutilisee pour toute l'application)
# ------------------------------------------------------------------------
@lru_cache
def obtenir_adaptateur_python_chess() -> AdaptateurPythonChess:
    return AdaptateurPythonChess()


@lru_cache
def obtenir_adaptateur_lichess() -> AdaptateurLichess:
    return AdaptateurLichess()


@lru_cache
def obtenir_adaptateur_polyglot() -> AdaptateurPolyglot:
    chemin_livre = os.getenv("POLYGLOT_BOOK_PATH") or (
        CHEMIN_LIVRE_POLYGLOT_PAR_DEFAUT
    )
    return AdaptateurPolyglot(chemin_livre=chemin_livre)


@lru_cache
def obtenir_adaptateur_theorie() -> AdaptateurTheorieAvecSecours:
    return AdaptateurTheorieAvecSecours(
        principal = obtenir_adaptateur_lichess(),
        secours   = obtenir_adaptateur_polyglot(),
    )


@lru_cache
def obtenir_adaptateur_stockfish() -> AdaptateurStockfish:
    # os.getenv(...) ne retombe sur le defaut QUE si la variable est
    # absente ; si STOCKFISH_PATH="" (vide) dans le .env, on retombe
    # aussi sur le defaut grace au "or" ci-dessous.
    chemin_binaire = os.getenv("STOCKFISH_PATH") or (
        CHEMIN_STOCKFISH_PAR_DEFAUT
    )
    return AdaptateurStockfish(chemin_binaire=chemin_binaire)


# ------------------------------------------------------------------------
# Cas d'utilisation (composent les ports via les adaptateurs ci-dessus)
# ------------------------------------------------------------------------
def obtenir_service_coups_theoriques() -> ObtenirCoupsTheoriquesService:
    return ObtenirCoupsTheoriquesService(
        validateur = obtenir_adaptateur_python_chess(),
        theorie    = obtenir_adaptateur_theorie(),
    )


def obtenir_service_evaluation() -> EvaluerPositionService:
    return EvaluerPositionService(
        validateur = obtenir_adaptateur_python_chess(),
        moteur     = obtenir_adaptateur_stockfish(),
    )


def obtenir_service_exploration() -> ExplorerPositionService:
    return ExplorerPositionService(
        service_coups      = obtenir_service_coups_theoriques(),
        service_evaluation = obtenir_service_evaluation(),
    )
