#!/usr/bin/env python
# ############################################################################
# Script de generation du schema du graphe LangGraph (docs/images/)
# ############################################################################
# Construit le graphe reel defini dans app/application/agent/graphe_agent.py
# et exporte sa structure en PNG, via l'utilitaire officiel de LangGraph
# (CompiledGraph.get_graph().draw_mermaid_png()). Aucune requete HTTP,
# aucun Stockfish/Milvus/Mongo requis : seule la topologie du graphe est
# inspectee, les noeuds ne sont jamais executes, donc les services
# d'application peuvent rester des simples marqueurs (None).
#
# Utilisation :
#   uv run python scripts/visualiser_graphe.py
#   uv run python scripts/visualiser_graphe.py --sortie chemin/personnalise.png

# Bibliotheque standard
import argparse    # Lecture des arguments de la ligne de commande
import sys         # Code de sortie du script
from   pathlib import Path    # Construction robuste de chemins

# Modules internes
from   app.application.agent.graphe_agent import construire_graphe

CHEMIN_SORTIE_PAR_DEFAUT = Path("docs/images/graphe_agent.png")


# ------------------------------------------------------------------------
# Construction du graphe (services factices : seule la structure importe)
# ------------------------------------------------------------------------
def construire_graphe_pour_visualisation():
    """Compile le graphe reel sans instancier les adaptateurs.

    Les noeuds ne sont jamais appeles ici : draw_mermaid_png() n'inspecte
    que les noms de noeuds et les aretes (dont les aretes conditionnelles
    de decider_apres_theorie), jamais le corps des fonctions. Passer None
    en guise de services est donc sans risque pour ce seul usage.
    """

    return construire_graphe(
        service_coups      = None,
        service_evaluation = None,
        service_contexte   = None,
        checkpointer        = None,
    )


# ------------------------------------------------------------------------
# Export en PNG (avec repli en Mermaid texte si l'export image echoue)
# ------------------------------------------------------------------------
def exporter_png(grafo, chemin_sortie: Path) -> bool:
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    try:
        donnees_png = grafo.get_graph().draw_mermaid_png()
    except Exception as erreur:    # noqa: BLE001 - export best-effort
        print(f"[ECHEC] export PNG impossible : {erreur}")
        print("        (draw_mermaid_png() appelle l'API mermaid.ink par")
        print("        defaut : verifier l'acces reseau sortant, ou")
        print("        installer Playwright pour un rendu local.)")

        chemin_repli = chemin_sortie.with_suffix(".mermaid")
        chemin_repli.write_text(grafo.get_graph().draw_mermaid())
        print(f"[ OK ] source Mermaid ecrite en repli : {chemin_repli}")
        return False

    chemin_sortie.write_bytes(donnees_png)
    print(f"[ OK ] schema du graphe ecrit : {chemin_sortie}")
    return True


# ------------------------------------------------------------------------
# Point d'entree
# ------------------------------------------------------------------------
def main() -> int:
    analyseur = argparse.ArgumentParser(
        description=(
            "Genere le schema PNG du graphe LangGraph de l'agent, a "
            "partir de sa definition reelle dans graphe_agent.py."
        ),
    )
    analyseur.add_argument(
        "--sortie", type=Path, default=CHEMIN_SORTIE_PAR_DEFAUT,
        help=f"Chemin du PNG genere (defaut: {CHEMIN_SORTIE_PAR_DEFAUT})",
    )
    arguments = analyseur.parse_args()

    grafo = construire_graphe_pour_visualisation()
    reussi = exporter_png(grafo, arguments.sortie)

    return 0 if reussi else 1


if __name__ == "__main__":
    sys.exit(main())
