#!/usr/bin/env python
# ############################################################################
# Inspecte le contenu REEL d'un checkpoint MongoDB pour un thread_id donne
# ############################################################################
# mongosh seul ne peut pas afficher ce contenu de facon lisible : le champ
# "checkpoint" est serialise en binaire (msgpack) par LangGraph. Ce script
# passe par l'API officielle (graphe.get_state / get_state_history), qui
# desserialise pour nous, et affiche le resultat en vertical via LogTool.
#
# IMPORTANT : construit le graphe avec des services a None (comme
# visualiser_graphe.py) et SEULEMENT le vrai checkpointer Mongo -- lire un
# checkpoint n'execute aucun noeud, donc Milvus/Stockfish/YouTube/Anthropic
# ne sont pas necessaires ici, uniquement Mongo. Evite de construire le
# graphe de production complet (obtenir_graphe_agent), qui echouerait sur
# la resolution DNS de "milvus-standalone" hors du reseau Docker.
#
# Depuis l'hote (hors Docker), Mongo doit etre joignable via son port
# expose. Si MONGO_URI dans .env pointe vers "mongodb://mongodb:27017"
# (hostname Docker interne), le definir pour CETTE session seulement :
#   PowerShell : $env:MONGO_URI = "mongodb://localhost:27017"
#   bash       : export MONGO_URI="mongodb://localhost:27017"
# Ne jamais mettre "localhost" dans le .env partage (casserait le backend
# en conteneur -- meme lecon que MILVUS_HOST).
#
# Utilisation :
#   uv run python scripts/inspeccionar_checkpoint.py --thread-id prueba-mongo-1
#   uv run python scripts/inspeccionar_checkpoint.py --thread-id prueba-mongo-1 --historique
#   uv run python scripts/inspeccionar_checkpoint.py --thread-id prueba-mongo-1 --graphe agent_llm

import argparse
import sys

from app.core.dependances import obtenir_checkpointer_agent
from app.application.agent.graphe_agent import construire_graphe
from app.application.agent.graphe_agent_llm import construire_graphe_llm
from app.tools.rafael.log_tool import LogTool

log = LogTool(origin="inspeccionar_checkpoint")


def construire_graphe_pour_lecture(nom_graphe: str):
    """Construit le graphe demande avec le VRAI checkpointer Mongo, mais
    des services factices (None) -- suffisant pour get_state/
    get_state_history, qui ne font que lire, jamais executer un noeud."""

    checkpointer = obtenir_checkpointer_agent()

    if nom_graphe == "agent":
        return construire_graphe(
            service_coups=None, 
            service_evaluation=None,
            service_contexte=None, 
            
            checkpointer=checkpointer,
        )

    return construire_graphe_llm(
        service_coups=None, 
        service_evaluation=None, 
        service_contexte=None,

        service_videos=None, 
        modele_decision=None, 

        checkpointer=checkpointer,
    )


def afficher_etat(valeurs: dict, etiquette: str) -> None:
    """Affiche l'etat (EtatAgent) en vertical, champ par champ."""
    log.LOG_DICT(valeurs, etiquette)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--thread-id", required=True,
        help="id_session utilise lors de l'appel a /agent/invoke ou /agent-llm/invoke",
    )
    analyseur.add_argument(
        "--graphe", choices=["agent", "agent_llm"], default="agent",
        help="Quel graphe interroger (defaut: agent)",
    )
    analyseur.add_argument(
        "--historique", action="store_true",
        help="Affiche TOUS les checkpoints du thread, pas seulement le dernier",
    )
    arguments = analyseur.parse_args()

    grafo = construire_graphe_pour_lecture(arguments.graphe)
    configuration = {"configurable": {"thread_id": arguments.thread_id}}

    if not arguments.historique:
        snapshot = grafo.get_state(configuration)

        if not snapshot.values:
            print(f"Aucun checkpoint trouve pour thread_id={arguments.thread_id!r}")
            return 1

        print(f"\nthread_id       : {arguments.thread_id}")
        print(f"checkpoint_id   : {snapshot.config['configurable'].get('checkpoint_id')}")
        print(f"prochain noeud  : {snapshot.next or '(aucun -- FIN atteinte)'}")
        print()
        afficher_etat(dict(snapshot.values), "EtatAgent (dernier checkpoint)")
        return 0

    historique = list(grafo.get_state_history(configuration))
    if not historique:
        print(f"Aucun checkpoint trouve pour thread_id={arguments.thread_id!r}")
        return 1

    print(f"\n{len(historique)} checkpoint(s) trouve(s) pour thread_id={arguments.thread_id!r}\n")

    for i, snapshot in enumerate(reversed(historique), start=1):
        print(f"--- Checkpoint {i}/{len(historique)} "
              f"(id={snapshot.config['configurable'].get('checkpoint_id')}) ---")
        afficher_etat(dict(snapshot.values), f"etape_{i}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
