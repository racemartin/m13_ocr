# ############################################################################
# Assemblage du graphe LangGraph de l'agent -- VARIANTE avec decision LLM
# ############################################################################
# Etend le flux de base (graphe_agent.py, inchange) avec deux noeuds
# supplementaires qui appellent un LLM : decider_video (l'agent choisit
# s'il vaut la peine de chercher une video) et generer_reponse (synthese
# pedagogique en langage naturel). Fichier separe a dessein : l'endpoint
# existant (POST /api/v1/agent/invoke, via construire_graphe) n'est
# jamais touche par ce qui se passe ici.

# Bibliotheques tierces
from   langchain_anthropic import ChatAnthropic                # Modele de decision
from   langgraph.checkpoint.base import BaseCheckpointSaver    # Type generique
from   langgraph.graph import END, StateGraph    # Graphe d'etats

# Modules internes
from   app.application.obtenir_coups_theoriques_service import (  # Cas
    ObtenirCoupsTheoriquesService,                                 # d'usage
)
from   app.application.evaluer_position_service import (    # Cas
    EvaluerPositionService,                                 # d'usage
)
from   app.application.rechercher_contexte_ouverture_service import (  # Cas
    RechercherContexteOuvertureService,                                 # RAG
)
from   app.application.rechercher_videos_service import (  # Cas
    RechercherVideosService,                                # d'usage
)
from   app.application.agent.etat_agent import EtatAgent    # Etat partage
from   app.application.agent.noeuds_agent import (    # Fabriques de noeuds
    decider_apres_theorie,
    fabriquer_noeud_evaluer_position,
    fabriquer_noeud_rechercher_contexte,
    fabriquer_noeud_rechercher_theorie,
)
from   app.application.agent.noeuds_agent_llm import (    # Noeuds LLM
    decider_apres_video,
    fabriquer_noeud_decider_video,
    fabriquer_noeud_generer_reponse,
    fabriquer_noeud_rechercher_videos,
)


# ##############################################################################
# Construction et compilation du graphe (variante LLM)
# ##############################################################################
def construire_graphe_llm(
    service_coups      : ObtenirCoupsTheoriquesService,
    service_evaluation : EvaluerPositionService,
    service_contexte   : RechercherContexteOuvertureService,
    service_videos      : RechercherVideosService,
    modele_decision      : ChatAnthropic,
    checkpointer          : BaseCheckpointSaver | None = None,
):
    """Construit et compile la variante du graphe avec decision LLM.

    Memes trois premiers noeuds que construire_graphe() (theorie,
    Stockfish, RAG), puis deux noeuds LLM supplementaires :

        rechercher_theorie
              |
        theorie trouvee ? ---- oui ---> rechercher_contexte
              |                                |
             non                       decider_video (LLM)
              |                                |
        evaluer_position                video utile ? -oui-> rechercher_videos
              |                                |                    |
              `-----> rechercher_contexte      `-non--> generer_reponse (LLM) <-'
                                                               |
                                                              FIN
    """

    # ----------------------------------------------------------------
    # 1. Declaration des noeuds
    # ----------------------------------------------------------------
    graphe = StateGraph(EtatAgent)

    graphe.add_node(
        "rechercher_theorie",
        fabriquer_noeud_rechercher_theorie(service_coups),
    )
    graphe.add_node(
        "evaluer_position",
        fabriquer_noeud_evaluer_position(service_evaluation),
    )
    graphe.add_node(
        "rechercher_contexte",
        fabriquer_noeud_rechercher_contexte(service_contexte),
    )
    graphe.add_node(
        "decider_video",
        fabriquer_noeud_decider_video(modele_decision),
    )
    graphe.add_node(
        "rechercher_videos",
        fabriquer_noeud_rechercher_videos(service_videos),
    )
    graphe.add_node(
        "generer_reponse",
        fabriquer_noeud_generer_reponse(modele_decision),
    )

    # ----------------------------------------------------------------
    # 2. Point d'entree et aretes
    # ----------------------------------------------------------------
    graphe.set_entry_point("rechercher_theorie")

    graphe.add_conditional_edges(
        "rechercher_theorie",
        decider_apres_theorie,
        {
            "contexte": "rechercher_contexte",
            "evaluer" : "evaluer_position",
        },
    )
    graphe.add_edge("evaluer_position", "rechercher_contexte")
    graphe.add_edge("rechercher_contexte", "decider_video")

    graphe.add_conditional_edges(
        "decider_video",
        decider_apres_video,
        {
            "rechercher": "rechercher_videos",
            "fin"       : "generer_reponse",
        },
    )
    graphe.add_edge("rechercher_videos", "generer_reponse")
    graphe.add_edge("generer_reponse", END)

    # ----------------------------------------------------------------
    # 3. Compilation, avec ou sans persistance Mongo
    # ----------------------------------------------------------------
    return graphe.compile(checkpointer=checkpointer)
