# ############################################################################
# Adaptateur d'infrastructure : persistance de l'etat de l'agent (MongoDB)
# ############################################################################
# Seul module du systeme qui importe pymongo pour le graphe LangGraph.
# Ne construit pas un adaptateur "maison" : s'appuie sur MongoDBSaver,
# l'implementation officielle de CheckpointSaver fournie par le paquet
# langgraph-checkpoint-mongodb, au meme titre qu'AdaptateurMilvus s'appuie
# sur pymilvus plutot que de reimplementer un client Milvus.

# Bibliotheques tierces
from   langgraph.checkpoint.mongodb import MongoDBSaver    # Checkpointer
from   pymongo import MongoClient    # Client MongoDB

# Modules internes
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="adaptateur_checkpointer_mongo")

NOM_BASE_PAR_DEFAUT = "ffe_agent_checkpoints"


# ##############################################################################
# Construction du checkpointer
# ##############################################################################
def construire_checkpointer_mongo(
    uri     : str,
    nom_bdd : str = NOM_BASE_PAR_DEFAUT,
) -> MongoDBSaver:
    """Instancie le checkpointer MongoDB utilise par le graphe LangGraph.

    Le graphe conserve, par id_session (thread_id LangGraph), l'historique
    des positions analysees et des reponses de l'agent. Les collections
    (checkpoints, writes) sont creees automatiquement au premier appel si
    elles n'existent pas encore.
    """

    log.START_ACTION(
        "adaptateur_checkpointer_mongo", "construire_checkpointer_mongo",
        "Connexion au checkpointer MongoDB de l'agent",
    )
    log.PARAMETER_VALUE("nom_bdd", nom_bdd)

    client = MongoClient(uri)

    log.FINISH_ACTION(
        "adaptateur_checkpointer_mongo", "construire_checkpointer_mongo",
        "Checkpointer pret",
    )
    return MongoDBSaver(client, db_name=nom_bdd)
