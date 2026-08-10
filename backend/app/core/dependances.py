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

# Bibliotheque tierce
from   dotenv import load_dotenv    # Charge .env dans os.environ
from   langchain_anthropic import ChatAnthropic    # Modele de decision (Anthropic)
from   langchain_google_genai import ChatGoogleGenerativeAI  # (Google, repli)

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
from   app.application.rechercher_contexte_ouverture_service import (  # Cas
    RechercherContexteOuvertureService,                                 # RAG
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
from   app.infrastructure.adaptateur_milvus import AdaptateurMilvus  # RAG
from   app.infrastructure.adaptateur_checkpointer_mongo import (  # Check-
    construire_checkpointer_mongo,                                 # pointer
)
from   app.application.agent.graphe_agent import construire_graphe  # Agent
from   app.application.agent.graphe_agent_llm import (  # Agent + LLM
    construire_graphe_llm,                                # (variante)
)
from   app.infrastructure.adaptateur_youtube import AdaptateurYoutube  # API
from   app.application.rechercher_videos_service import (              # Cas
    RechercherVideosService,                                            # usage
)

# NOTE : necessaire pour que os.getenv(...) trouve les variables (MONGO_URI,
# YOUTUBE_API_KEY, STOCKFISH_PATH...) en local (uv run ...), pas seulement
# dans Docker (ou docker-compose injecte deja .env via "env_file:"). Place
# apres les imports (et non avant) pour ne pas declencher E402 de ruff.
load_dotenv()

# Chemin par defaut du binaire Stockfish dans l'image Docker (Debian/apt)
CHEMIN_STOCKFISH_PAR_DEFAUT = "/usr/games/stockfish"

# Chemin par defaut du livre Polyglot de secours (relatif a app/core/)
CHEMIN_LIVRE_POLYGLOT_PAR_DEFAUT = str(
    Path(__file__).resolve().parent.parent.parent
    / "data" / "polyglot" / "livre_ouvertures.bin"
)

# Parametres par defaut de la base vectorielle (Etape 3)
MILVUS_HOTE_PAR_DEFAUT   = "milvus-standalone"
MILVUS_PORT_PAR_DEFAUT   = "19530"
MODELE_EMBEDDINGS_PAR_DEFAUT = "paraphrase-multilingual-MiniLM-L12-v2"

# Parametre par defaut de connexion MongoDB (persistance de l'agent)
MONGO_URI_PAR_DEFAUT = "mongodb://mongodb:27017"

# Modele leger, suffisant pour une decision structuree simple (pas de
# generation de prose longue) -- pas besoin du modele le plus capable ici.
MODELE_DECISION_PAR_DEFAUT = "claude-haiku-4-5-20251001"


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


@lru_cache
def obtenir_adaptateur_youtube() -> AdaptateurYoutube:
    cle_api = os.getenv("YOUTUBE_API_KEY")
    if not cle_api:
        raise RuntimeError(
            "YOUTUBE_API_KEY absente : voir .env.example (Etape 4, "
            "cle API YouTube Data v3 requise)."
        )
    return AdaptateurYoutube(cle_api=cle_api)


def obtenir_service_videos() -> RechercherVideosService:
    return RechercherVideosService(
        recherche_videos=obtenir_adaptateur_youtube(),
    )


@lru_cache
def obtenir_adaptateur_milvus() -> AdaptateurMilvus:
    # NOTE : la connexion a Milvus et le chargement du modele d'embeddings
    # se font ici, au premier appel (via @lru_cache) -- pas a l'import du
    # module. Operation relativement lente (quelques secondes), executee
    # une seule fois pour toute la duree de vie de l'application.
    return AdaptateurMilvus(
        hote                   = os.getenv("MILVUS_HOST") or MILVUS_HOTE_PAR_DEFAUT,
        port                   = os.getenv("MILVUS_PORT") or MILVUS_PORT_PAR_DEFAUT,
        nom_modele_embeddings  = os.getenv("EMBEDDING_MODEL_NAME")
                                  or MODELE_EMBEDDINGS_PAR_DEFAUT,
    )


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


def obtenir_service_recherche_contexte() -> RechercherContexteOuvertureService:
    return RechercherContexteOuvertureService(
        base_connaissances = obtenir_adaptateur_milvus(),
    )


# ------------------------------------------------------------------------
# Agent LangGraph (compose les trois services existants + Mongo)
# ------------------------------------------------------------------------
@lru_cache
def obtenir_checkpointer_agent():
    uri = os.getenv("MONGO_URI") or MONGO_URI_PAR_DEFAUT
    return construire_checkpointer_mongo(uri=uri)


@lru_cache
def obtenir_modele_decision():
    """Construit le modele de decision, avec le fournisseur choisi par
    LLM_PROVIDER ("anthropic" par defaut, ou "google" en repli).

    Interchangeable a dessein : noeuds_agent_llm.py n'utilise que
    .with_structured_output() et .invoke(), l'interface commune a tous
    les Chat Models LangChain -- aucun code ne depend d'Anthropic
    specifiquement, seule CETTE fabrique choisit le fournisseur.
    """
    fournisseur = (os.getenv("LLM_PROVIDER") or "anthropic").lower()

    if fournisseur == "google":
        nom_modele = os.getenv("GOOGLE_MODEL") or "gemini-flash-latest"
        # GOOGLE_API_KEY est lue automatiquement depuis l'environnement.
        return ChatGoogleGenerativeAI(model=nom_modele)

    nom_modele = os.getenv("ANTHROPIC_MODEL") or MODELE_DECISION_PAR_DEFAUT
    # ANTHROPIC_API_KEY est lue automatiquement par ChatAnthropic depuis
    # l'environnement (deja charge par load_dotenv() plus haut) -- pas
    # besoin de la passer explicitement ici.
    return ChatAnthropic(model=nom_modele, temperature=0.0)


@lru_cache
def obtenir_graphe_agent():
    return construire_graphe(
        service_coups      = obtenir_service_coups_theoriques(),
        service_evaluation = obtenir_service_evaluation(),
        service_contexte   = obtenir_service_recherche_contexte(),
        checkpointer        = obtenir_checkpointer_agent(),
    )


@lru_cache
def obtenir_graphe_agent_llm():
    return construire_graphe_llm(
        service_coups      = obtenir_service_coups_theoriques(),
        service_evaluation = obtenir_service_evaluation(),
        service_contexte   = obtenir_service_recherche_contexte(),
        service_videos      = obtenir_service_videos(),
        modele_decision      = obtenir_modele_decision(),
        checkpointer          = obtenir_checkpointer_agent(),
    )
