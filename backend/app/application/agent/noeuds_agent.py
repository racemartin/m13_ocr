# ############################################################################
# Noeuds du graphe LangGraph de l'agent
# ############################################################################
# Chaque noeud est une fonction pure qui recoit l'EtatAgent courant et
# retourne uniquement les cles qu'il modifie (les mises a jour partielles
# sont fusionnees automatiquement par LangGraph dans l'etat global).
#
# Aucun noeud n'appelle directement une bibliotheque d'infrastructure :
# chacun delegue a un service d'application deja existant et deja teste
# (ObtenirCoupsTheoriquesService, EvaluerPositionService,
# RechercherContexteOuvertureService). LangGraph n'est donc qu'un
# mecanisme d'enchainement supplementaire dans la couche application, au
# meme titre que ExplorerPositionService -- pas une nouvelle couche
# d'acces a l'infrastructure.

# Bibliotheque standard
from   typing import Callable, Literal    # Typage des fabriques de noeuds

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
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="noeuds_agent")


# ##############################################################################
# Noeud : recherche des coups theoriques (Lichess -> secours Polyglot)
# ##############################################################################
def fabriquer_noeud_rechercher_theorie(
    service: ObtenirCoupsTheoriquesService,
) -> Callable[[EtatAgent], dict]:
    """Construit le noeud de recherche des coups theoriques."""

    def noeud_rechercher_theorie(etat: EtatAgent) -> dict:
        log.START_ACTION(
            "noeud_rechercher_theorie", "executer",
            "Recherche des coups theoriques connus pour la position",
        )
        log.PARAMETER_VALUE("fen", etat["fen"])

        coups = service.executer(etat["fen"])

        log.FINISH_ACTION(
            "noeud_rechercher_theorie", "executer",
            f"{len(coups)} coup(s) theorique(s) trouve(s)",
        )
        return {"coups_theoriques": coups}

    return noeud_rechercher_theorie


# ##############################################################################
# Noeud : evaluation Stockfish, appele uniquement si aucune theorie trouvee
# ##############################################################################
def fabriquer_noeud_evaluer_position(
    service: EvaluerPositionService,
) -> Callable[[EtatAgent], dict]:
    """Construit le noeud d'evaluation par le moteur Stockfish."""

    def noeud_evaluer_position(etat: EtatAgent) -> dict:
        log.LEVEL_6_NOTICE(
            "noeud_evaluer_position",
            f"Aucune theorie pour {etat['fen']}, appel au moteur Stockfish",
        )

        evaluation = service.executer(etat["fen"])

        log.FINISH_ACTION(
            "noeud_evaluer_position", "executer",
            f"Evaluation : {evaluation.type}={evaluation.valeur}",
        )
        return {"evaluation": evaluation}

    return noeud_evaluer_position


# ##############################################################################
# Noeud : recherche de contexte pedagogique (RAG, Milvus)
# ##############################################################################
def fabriquer_noeud_rechercher_contexte(
    service: RechercherContexteOuvertureService,
) -> Callable[[EtatAgent], dict]:
    """Construit le noeud de recherche vectorielle de contexte."""

    def noeud_rechercher_contexte(etat: EtatAgent) -> dict:
        requete = _construire_requete_contexte(etat)

        log.START_ACTION(
            "noeud_rechercher_contexte", "executer",
            "Recherche de contexte pedagogique (RAG)",
        )
        log.PARAMETER_VALUE("requete", requete)

        contexte = service.executer(requete)

        log.FINISH_ACTION(
            "noeud_rechercher_contexte", "executer",
            f"{len(contexte)} extrait(s) trouve(s)",
        )
        return {"contexte_ouverture": contexte}

    return noeud_rechercher_contexte


# ------------------------------------------------------------------------
# Construction de la requete texte envoyee au RAG
# ------------------------------------------------------------------------
def _construire_requete_contexte(etat: EtatAgent) -> str:
    """Determine le texte de recherche envoye a Milvus.

    LIMITE CONNUE : ni le FEN ni les coups theoriques suivants ne
    donnent directement le *nom* de l'ouverture deja jouee (le mapping
    FEN/moves_pgn -> nom ECO reste a construire, cf. la note du
    document technique sur les codes ECO non uniques). En l'absence de
    ce mapping, on retombe sur le FEN brut : la recherche vectorielle
    reste possible mais moins pertinente qu'une requete par nom
    d'ouverture. A ameliorer une fois la resolution ECO disponible.
    """

    return etat["fen"]


# ##############################################################################
# Arete conditionnelle : theorie trouvee ou non
# ##############################################################################
def decider_apres_theorie(etat: EtatAgent) -> Literal["contexte", "evaluer"]:
    """Reproduit la bifurcation deja codee a la main dans
    ExplorerPositionService (/explore/{fen})."""

    if etat.get("coups_theoriques"):
        return "contexte"  # Theorie connue -> pas besoin de Stockfish
    return "evaluer"       # Hors theorie -> evaluation moteur necessaire
