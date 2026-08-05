"""
diagnostico_grafo_llm.py -- inspecciona el grafo LLM REAL de tu proyecto,
tal como esta en disco ahora mismo, sin asumir nada de versiones
anteriores de los ficheros.

Uso (desde backend/):
    uv run python diagnostico_grafo_llm.py
"""

import sys
sys.path.insert(0, "tests")

from app.application.obtenir_coups_theoriques_service import (
    ObtenirCoupsTheoriquesService,
)
from app.application.evaluer_position_service import EvaluerPositionService
from app.application.rechercher_contexte_ouverture_service import (
    RechercherContexteOuvertureService,
)
from app.application.rechercher_videos_service import RechercherVideosService
from app.application.agent.graphe_agent_llm import construire_graphe_llm
from app.application.agent.noeuds_agent_llm import DecisionVideo
from app.domaine.modeles import CoupTheorique, ExtraitConnaissance
from fakes import (
    FauxValidateurEchecs, FauxTheorieOuvertures, FauxMoteurEvaluation,
    FauxBaseConnaissances, FauxRechercheVideos, FauxModeleDecision,
)

print("=" * 70)
print("1. DE QUEL FICHIER vient exactement chaque fonction importee")
print("=" * 70)
print("construire_graphe_llm  ->", construire_graphe_llm.__module__)
print("DecisionVideo          ->", DecisionVideo.__module__)

print()
print("=" * 70)
print("2. CONSTRUCTION du graphe (avec decision=True force)")
print("=" * 70)
sc = ObtenirCoupsTheoriquesService(
    validateur=FauxValidateurEchecs(),
    theorie=FauxTheorieOuvertures(coups=[
        CoupTheorique(uci="e2e4", san="e4", nombre_parties=1),
    ]),
)
se = EvaluerPositionService(
    validateur=FauxValidateurEchecs(),
    moteur=FauxMoteurEvaluation(evaluation=None),
)
sr = RechercherContexteOuvertureService(
    base_connaissances=FauxBaseConnaissances(extraits=[
        ExtraitConnaissance(
            texte="...", ouverture="Sicilienne",
            source_url="https://fr.wikipedia.org/...", score=0.9,
        ),
    ]),
)
sv = RechercherVideosService(
    recherche_videos=FauxRechercheVideos(videos=[]),
)
md = FauxModeleDecision(
    decision=DecisionVideo(rechercher_video=True, requete_video="Sicilienne"),
)

grafo = construire_graphe_llm(sc, se, sr, sv, md, checkpointer=None)

print()
print("=" * 70)
print("3. STRUCTURE REELLE du graphe compile (get_graph())")
print("=" * 70)
structure = grafo.get_graph()
print("Noeuds:", list(structure.nodes.keys()))
print()
print("Aretes:")
for arete in structure.edges:
    etiquette = f"  [{arete.conditional}]" if arete.conditional else ""
    print(f"  {arete.source} -> {arete.target}{etiquette}")

print()
print("=" * 70)
print("4. INVOCATION reelle, avec impression du resultat brut")
print("=" * 70)
resultat = grafo.invoke({
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
})
print()
print("Cles presentes dans le resultat final:", sorted(resultat.keys()))
print("rechercher_video =", resultat.get("rechercher_video", "<<< ABSENT >>>"))
