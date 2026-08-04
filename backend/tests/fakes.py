# ############################################################################
# Doublures de test (fakes) implementant les ports du domaine
# ############################################################################
# Permettent de tester les endpoints sans dependre du reseau (Lichess) ni
# d'un binaire Stockfish installe : on injecte ces fakes a la place des
# vrais adaptateurs, via les dependency_overrides de FastAPI.

# Modules internes
from   app.domaine.modeles import (    # Modeles
    CoupTheorique, Evaluation, ExtraitConnaissance, VideoExplicative,
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

    def indexer_documents(self, dossier: str) -> int:
        return len(self.extraits)

    def rechercher_contexte(
        self, requete: str, top_k: int = 3,
    ) -> list[ExtraitConnaissance]:
        return self.extraits[:top_k]


class FauxRechercheVideos(PortRechercheVideos):
    """Simule l'API YouTube sans consommer de quota reel."""

    def __init__(self, videos: list[VideoExplicative] | None = None) -> None:
        self.videos = videos if videos is not None else []

    def rechercher(
        self, requete: str, max_resultats: int = 5,
    ) -> list[VideoExplicative]:
        return self.videos[:max_resultats]
