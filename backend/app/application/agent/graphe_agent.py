# ############################################################################
# Assemblage du graphe LangGraph de l'agent
# ############################################################################
# Une seule fonction publique, construire_graphe(...), recoit les services
# d'application deja instancies (meme pattern d'injection que les autres
# cas d'utilisation composes, cf. ExplorerPositionService) et retourne le
# graphe compile, pret a etre invoque par la couche API.

# Bibliotheques tierces
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
from   app.application.agent.etat_agent import EtatAgent    # Etat partage
from   app.application.agent.noeuds_agent import (    # Fabriques de noeuds
    decider_apres_theorie,
    fabriquer_noeud_evaluer_position,
    fabriquer_noeud_rechercher_contexte,
    fabriquer_noeud_rechercher_theorie,
)


# ##############################################################################
# Construction et compilation du graphe
# ##############################################################################
def construire_graphe(
    service_coups      : ObtenirCoupsTheoriquesService,
    service_evaluation : EvaluerPositionService,
    service_contexte   : RechercherContexteOuvertureService,
    checkpointer        : BaseCheckpointSaver | None = None,
):
    """Construit et compile le graphe de l'agent.

    Reproduit exactement le flux deja code a la main dans
    ExplorerPositionService, en y ajoutant systematiquement la recherche
    de contexte RAG (Etape 3), theorie trouvee ou non :

        rechercher_theorie
              |
        theorie trouvee ? ---- oui ---> rechercher_contexte -> FIN
              |
             non
              |
        evaluer_position -> rechercher_contexte -> FIN

    Si un checkpointer est fourni (MongoDBSaver), l'etat est persiste par
    id_session (thread_id LangGraph) : un meme fil de conversation
    retrouve son historique entre deux appels.
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
    graphe.add_edge("rechercher_contexte", END)

    # ----------------------------------------------------------------
    # 3. Compilation, avec ou sans persistance Mongo
    # ----------------------------------------------------------------
    return graphe.compile(checkpointer=checkpointer)
