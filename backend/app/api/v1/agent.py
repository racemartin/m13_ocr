# ############################################################################
# Route : agent complet (theorie ou moteur, puis contexte RAG) -- SANS LLM
# ############################################################################
# Traduit la requete HTTP vers le graphe LangGraph de base. A la difference
# de /explore/{fen}, cette route enrichit toujours la reponse avec le
# contexte pedagogique RAG de l'Etape 3, et persiste l'etat de la
# conversation par id_session dans MongoDB.
#
# NOTE : reste volontairement inchange depuis sa version initiale. La
# variante avec decision LLM (video + synthese pedagogique) vit a part,
# dans agent_llm.py -- voir POST /api/v1/agent-llm/invoke.

# Bibliotheques tierces
from   fastapi import APIRouter, Depends, HTTPException    # Framework web
from   pydantic import BaseModel    # Schema de requete

# Modules internes
from   app.api.v1.schemas import (    # Schema HTTP
    CoupTheoriqueSchema, EvaluationSchema, ExtraitConnaissanceSchema,
    InfoEcoSchema,
)
from   app.core.dependances import obtenir_graphe_agent    # Injection
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

routeur = APIRouter()
log     = LogTool(origin="api.agent")


class RequeteAgent(BaseModel):
    """Schema HTTP de la requete envoyee a l'agent."""

    fen        : str    # Position courante, notation FEN
    id_session : str    # Identifiant de conversation (thread_id LangGraph)


class ReponseAgent(BaseModel):
    """Schema HTTP de la reponse de l'agent."""

    fen                : str
    eco                : InfoEcoSchema | None             = None
    coups_theoriques   : list[CoupTheoriqueSchema]       = []
    evaluation         : EvaluationSchema | None         = None
    contexte_ouverture : list[ExtraitConnaissanceSchema] = []


# ##############################################################################
# Endpoint : invocation complete de l'agent
# ##############################################################################
@routeur.post("/agent/invoke", response_model=ReponseAgent)
def invoquer_agent(
    requete : RequeteAgent,
    graphe  = Depends(obtenir_graphe_agent),
) -> ReponseAgent:
    """Invoque le graphe LangGraph pour une position donnee.

    Combine, selon le cas, les coups theoriques ou l'evaluation
    Stockfish, ainsi que le contexte pedagogique RAG.
    """
    configuration = {"configurable": {"thread_id": requete.id_session}}

    log.START_ACTION(
        "invoquer_agent", "POST /api/v1/agent/invoke",
        f"Invocation du graphe (id_session={requete.id_session})",
    )
    log.PARAMETER_VALUE("fen", requete.fen)

    try:
        resultat = graphe.invoke(
            {"fen": requete.fen, "id_session": requete.id_session},
            config=configuration,
        )
    except ValueError as erreur:
        log.LEVEL_6_NOTICE("invoquer_agent", f"FEN invalide : {erreur}")
        raise HTTPException(status_code=422, detail=str(erreur)) from erreur

    log.FINISH_ACTION(
        "invoquer_agent", "POST /api/v1/agent/invoke",
        f"{len(resultat.get('coups_theoriques') or [])} coup(s) theorique(s), "
        f"evaluation={'oui' if resultat.get('evaluation') else 'non'}, "
        f"{len(resultat.get('contexte_ouverture') or [])} extrait(s) RAG",
    )

    evaluation = resultat.get("evaluation")
    eco = resultat.get("eco")

    return ReponseAgent(
        fen                = requete.fen,
        eco                = InfoEcoSchema.depuis_domaine(eco) if eco else None,
        coups_theoriques   = [
            CoupTheoriqueSchema.depuis_domaine(coup)
            for coup in resultat.get("coups_theoriques") or []
        ],
        evaluation         = (
            EvaluationSchema.depuis_domaine(requete.fen, evaluation)
            if evaluation else None
        ),
        contexte_ouverture = [
            ExtraitConnaissanceSchema.depuis_domaine(extrait)
            for extrait in resultat.get("contexte_ouverture") or []
        ],
    )
