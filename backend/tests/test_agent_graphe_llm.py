# ############################################################################
# Tests : graphe LangGraph -- variante avec decision LLM
# ############################################################################
# (app/application/agent/graphe_agent_llm.py). Utilise FauxModeleDecision :
# aucun appel a l'API Anthropic dans ces tests. Complementaire de
# test_agent_graphe.py, qui couvre la version de base (sans LLM).

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
from   app.application.agent.graphe_agent_llm import construire_graphe_llm
from   app.application.agent.noeuds_agent_llm import DecisionVideo
from   app.domaine.modeles import (
    CoupTheorique, Evaluation, ExtraitConnaissance, VideoExplicative,
)
from   tests.conftest import FEN_POSITION_DEPART
from   tests.fakes import (
    FauxValidateurEchecs, FauxTheorieOuvertures, FauxMoteurEvaluation,
    FauxBaseConnaissances, FauxRechercheVideos, FauxModeleDecision,
)


def construire_graphe_llm_de_test(
    coups=None, evaluation=None, extraits=None, videos=None,
    decision_video=None, texte_genere="Explication de test.",
    fen_valide=True,
):
    service_coups = ObtenirCoupsTheoriquesService(
        validateur = FauxValidateurEchecs(fen_valide=fen_valide),
        theorie    = FauxTheorieOuvertures(coups=coups or []),
    )
    service_evaluation = EvaluerPositionService(
        validateur = FauxValidateurEchecs(fen_valide=fen_valide),
        moteur     = FauxMoteurEvaluation(evaluation=evaluation),
    )
    service_contexte = RechercherContexteOuvertureService(
        base_connaissances = FauxBaseConnaissances(extraits=extraits or []),
    )
    service_videos = RechercherVideosService(
        recherche_videos = FauxRechercheVideos(videos=videos or []),
    )
    modele_decision = FauxModeleDecision(
        decision=decision_video, texte_genere=texte_genere,
    )

    return construire_graphe_llm(
        service_coups      = service_coups,
        service_evaluation = service_evaluation,
        service_contexte   = service_contexte,
        service_videos      = service_videos,
        modele_decision      = modele_decision,
        checkpointer          = None,
    )


def test_graphe_llm_recherche_video_quand_le_llm_decide_oui():
    extraits = [
        ExtraitConnaissance(
            texte="...", ouverture="Sicilienne",
            source_url="https://fr.wikipedia.org/...", score=0.9,
        ),
    ]
    videos = [
        VideoExplicative(
            id_video="abc123", titre="Sicilian Defense Explained",
            chaine="GothamChess",
            url="https://www.youtube.com/watch?v=abc123", vues=890_000,
        ),
    ]
    graphe = construire_graphe_llm_de_test(
        coups=[CoupTheorique(uci="e2e4", san="e4", nombre_parties=1)],
        extraits=extraits, videos=videos,
        decision_video=DecisionVideo(
            rechercher_video=True, requete_video="Sicilienne",
        ),
    )

    resultat = graphe.invoke({"fen": FEN_POSITION_DEPART})

    assert resultat["rechercher_video"] is True
    assert resultat["requete_video"] == "Sicilienne"
    assert resultat["videos"] == videos


def test_graphe_llm_ne_cherche_pas_de_video_quand_le_llm_decide_non():
    graphe = construire_graphe_llm_de_test(
        coups=[CoupTheorique(uci="e2e4", san="e4", nombre_parties=1)],
        videos=[VideoExplicative(   # present cote fake, mais ne doit PAS
            id_video="xxx", titre="...", chaine="...",  # etre atteint
            url="https://www.youtube.com/watch?v=xxx",
        )],
        decision_video=DecisionVideo(rechercher_video=False, requete_video=""),
    )

    resultat = graphe.invoke({"fen": FEN_POSITION_DEPART})

    assert resultat["rechercher_video"] is False
    # Le noeud rechercher_videos n'a jamais tourne : la cle est absente,
    # pas juste vide -- distinction importante (cf. total=False de EtatAgent)
    assert "videos" not in resultat


def test_graphe_llm_genere_une_explication_en_langage_naturel():
    graphe = construire_graphe_llm_de_test(
        coups=[CoupTheorique(uci="e2e4", san="e4", nombre_parties=1)],
        decision_video=DecisionVideo(rechercher_video=False, requete_video=""),
        texte_genere="La Sicilienne est un excellent choix pour contre-attaquer.",
    )

    resultat = graphe.invoke({"fen": FEN_POSITION_DEPART})

    assert resultat["explication"] == (
        "La Sicilienne est un excellent choix pour contre-attaquer."
    )


def test_graphe_llm_se_degrade_si_le_modele_echoue():
    """Si le modele de decision leve une exception, le graphe retombe
    sur l'heuristique de repli plutot que de planter."""

    class ModeleQuiEchoue:
        def with_structured_output(self, schema):
            return self

        def invoke(self, prompt):
            raise RuntimeError("cle API invalide (simulation)")

    service_coups = ObtenirCoupsTheoriquesService(
        validateur = FauxValidateurEchecs(),
        theorie    = FauxTheorieOuvertures(coups=[]),
    )
    service_evaluation = EvaluerPositionService(
        validateur = FauxValidateurEchecs(),
        moteur     = FauxMoteurEvaluation(evaluation=Evaluation(
            type="cp", valeur=10, coup_recommande="e2e4", profondeur=10,
        )),
    )
    extraits = [ExtraitConnaissance(
        texte="...", ouverture="Sicilienne",
        source_url="https://fr.wikipedia.org/...", score=0.9,
    )]
    service_contexte = RechercherContexteOuvertureService(
        base_connaissances = FauxBaseConnaissances(extraits=extraits),
    )
    service_videos = RechercherVideosService(
        recherche_videos = FauxRechercheVideos(videos=[]),
    )

    graphe = construire_graphe_llm(
        service_coups      = service_coups,
        service_evaluation = service_evaluation,
        service_contexte   = service_contexte,
        service_videos      = service_videos,
        modele_decision      = ModeleQuiEchoue(),
        checkpointer          = None,
    )

    # Ne doit PAS lever d'exception malgre l'echec du LLM
    resultat = graphe.invoke({"fen": FEN_POSITION_DEPART})

    # Repli : rechercher_video=True car il y a du contexte RAG (cf.
    # heuristique de secours dans noeuds_agent_llm.py)
    assert resultat["rechercher_video"] is True
    assert resultat["requete_video"] == "Sicilienne"
