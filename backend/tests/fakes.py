# ############################################################################
# Doublures de test (fakes) implementant les ports du domaine
# ############################################################################
# Permettent de tester les endpoints sans dependre du reseau (Lichess) ni
# d'un binaire Stockfish installe : on injecte ces fakes a la place des
# vrais adaptateurs, via les dependency_overrides de FastAPI.

# Modules internes
from   app.domaine.modeles import (    # Modeles
    CoupTheorique, Evaluation, ExtraitConnaissance, InfoEco, VideoExplicative,
)
from   app.domaine.ports.port_validateur_echecs import (       # Ports
    PortValidateurEchecs,
)
from   app.domaine.ports.port_theorie_ouvertures import (
    PortTheorieOuvertures,
)
from   app.domaine.ports.port_moteur_evaluation import (
    PortMoteurEvaluation,
)
from   app.domaine.ports.port_base_connaissances import (
    PortBaseConnaissances,
)
from   app.domaine.ports.port_recherche_videos import (
    PortRechercheVideos,
)
from   app.domaine.ports.port_identification_eco import (
    PortIdentificationEco,
)


class FauxValidateurEchecs(PortValidateurEchecs):
    """Simule la validation de FEN sans appeler python-chess."""

    def __init__(self, fen_valide: bool = True) -> None:
        self.fen_valide = fen_valide

    def valider_fen(self, fen: str) -> bool:
        return self.fen_valide

    def coups_legaux(self, fen: str) -> list[str]:
        return []


class FauxTheorieOuvertures(PortTheorieOuvertures):
    """Simule l'API Lichess en retournant une liste fixe de coups."""

    def __init__(self, coups: list[CoupTheorique] | None = None) -> None:
        self.coups = coups if coups is not None else []

    def coups_theoriques(self, fen: str) -> list[CoupTheorique]:
        return self.coups


class FauxMoteurEvaluation(PortMoteurEvaluation):
    """Simule Stockfish en retournant une evaluation fixe."""

    def __init__(self, evaluation: Evaluation | None = None) -> None:
        self.evaluation = evaluation or Evaluation(type="cp", valeur=0)

    def evaluer(self, fen: str) -> Evaluation:
        return self.evaluation


class FauxBaseConnaissances(PortBaseConnaissances):
    """Simule Milvus sans dependre d'un serveur reel ni d'un modele."""

    def __init__(self, extraits: list[ExtraitConnaissance] | None = None) -> None:
        self.extraits = extraits if extraits is not None else []
        self.derniere_requete: str | None = None    # Pour verifier la requete envoyee

    def indexer_documents(self, dossier: str) -> int:
        return len(self.extraits)

    def rechercher_contexte(
        self, requete: str, top_k: int = 3,
    ) -> list[ExtraitConnaissance]:
        self.derniere_requete = requete
        return self.extraits[:top_k]


class FauxRechercheVideos(PortRechercheVideos):
    """Simule l'API YouTube sans consommer de quota reel."""

    def __init__(self, videos: list[VideoExplicative] | None = None) -> None:
        self.videos = videos if videos is not None else []

    def rechercher(
        self, requete: str, max_resultats: int = 5,
    ) -> list[VideoExplicative]:
        return self.videos[:max_resultats]


class FauxIdentificationEco(PortIdentificationEco):
    """Simule l'index ECO sans lire de fichier reel."""

    def __init__(self, resultat: InfoEco | None = None) -> None:
        self.resultat = resultat

    def identifier(self, fen: str) -> InfoEco | None:
        return self.resultat


class FauxModeleDecision:
    """Simule ChatAnthropic sans appel reseau ni cle API, pour les DEUX
    usages reels du modele dans le graphe :
      - with_structured_output(...).invoke(...) -> decision structuree
      - invoke(...) direct                       -> texte libre (.content)
    """

    def __init__(
        self, decision=None, texte_genere: str = "Explication de test.",
    ) -> None:
        from app.application.agent.noeuds_agent_llm import DecisionVideo
        self.decision = decision or DecisionVideo(
            rechercher_video=True, requete_video="Sicilienne",
        )
        self.texte_genere = texte_genere

    def with_structured_output(self, schema):
        return _FauxSortieStructuree(self.decision)

    def invoke(self, prompt: str):
        return _FauxMessageIA(self.texte_genere)


class _FauxSortieStructuree:
    """Retour de with_structured_output(...) : renvoie l'objet Pydantic
    directement, comme le fait le vrai ChatAnthropic."""

    def __init__(self, decision) -> None:
        self.decision = decision

    def invoke(self, prompt: str):
        return self.decision


class _FauxMessageIA:
    """Imite AIMessage : seul `.content` est utilise par nos noeuds."""

    def __init__(self, content: str) -> None:
        self.content = content
