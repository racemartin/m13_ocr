# ############################################################################
# Route : agent complet -- VARIANTE avec decision LLM (video + synthese)
# ############################################################################
# Meme contrat d'entree que POST /api/v1/agent/invoke, mais utilise le
# graphe etendu (graphe_agent_llm.py) : le LLM decide s'il faut chercher
# une video, et genere une explication pedagogique en langage naturel.
#
# N'affecte jamais /api/v1/agent/invoke : routeur, graphe et checkpointer
# sont bien distincts (voir dependances.py : obtenir_graphe_agent_llm()).

# Bibliotheques tierces
from   fastapi import APIRouter, Depends, HTTPException    # Framework web
from   pydantic import BaseModel    # Schema de requete

# Modules internes
from   app.api.v1.schemas import (    # Schema HTTP
    CoupTheoriqueSchema, EvaluationSchema, ExtraitConnaissanceSchema,
    InfoEcoSchema,
)
from   app.api.v1.videos import VideoSchema    # Reutilise le schema existant
from   app.core.dependances import obtenir_graphe_agent_llm    # Injection
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

routeur = APIRouter()
log     = LogTool(origin="api.agent_llm")


class RequeteAgentLLM(BaseModel):
    """Schema HTTP de la requete envoyee a l'agent (variante LLM)."""

    fen        : str    # Position courante, notation FEN
    id_session : str    # Identifiant de conversation (thread_id LangGraph)


class ReponseAgentLLM(BaseModel):
    """Schema HTTP de la reponse de l'agent (variante LLM)."""

    fen                : str
    eco                : InfoEcoSchema | None             = None
    coups_theoriques   : list[CoupTheoriqueSchema]       = []
    evaluation         : EvaluationSchema | None         = None
    contexte_ouverture : list[ExtraitConnaissanceSchema] = []
    videos             : list[VideoSchema]               = []
    explication        : str | None                      = None


# ##############################################################################
# Endpoint : invocation complete de l'agent, avec decision LLM
# ##############################################################################
@routeur.post("/agent-llm/invoke", response_model=ReponseAgentLLM)
def invoquer_agent_llm(
    requete : RequeteAgentLLM,
    graphe  = Depends(obtenir_graphe_agent_llm),
) -> ReponseAgentLLM:
    """Invoque le graphe LangGraph etendu (avec decision LLM) pour une
    position donnee.

    A la difference de /agent/invoke, cette route laisse un LLM decider
    s'il vaut la peine de chercher une video explicative, et synthetise
    une explication pedagogique en langage naturel.
    """
    configuration = {"configurable": {"thread_id": requete.id_session}}

    log.START_ACTION(
        "invoquer_agent_llm", "POST /api/v1/agent-llm/invoke",
        f"Invocation du graphe LLM (id_session={requete.id_session})",
    )
    log.PARAMETER_VALUE("fen", requete.fen)

    try:
        resultat = graphe.invoke(
            {"fen": requete.fen, "id_session": requete.id_session},
            config=configuration,
        )
    except ValueError as erreur:
        log.LEVEL_6_NOTICE("invoquer_agent_llm", f"FEN invalide : {erreur}")
        raise HTTPException(status_code=422, detail=str(erreur)) from erreur

    log.FINISH_ACTION(
        "invoquer_agent_llm", "POST /api/v1/agent-llm/invoke",
        f"{len(resultat.get('coups_theoriques') or [])} coup(s) theorique(s), "
        f"evaluation={'oui' if resultat.get('evaluation') else 'non'}, "
        f"{len(resultat.get('contexte_ouverture') or [])} extrait(s) RAG, "
        f"{len(resultat.get('videos') or [])} video(s), "
        f"explication={'oui' if resultat.get('explication') else 'non'}",
    )

    evaluation = resultat.get("evaluation")
    eco = resultat.get("eco")

    return ReponseAgentLLM(
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
        videos             = [
            VideoSchema(
                id_video=v.id_video, titre=v.titre,
                chaine=v.chaine, url=v.url, vues=v.vues,
            )
            for v in resultat.get("videos") or []
        ],
        explication        = resultat.get("explication"),
    )
