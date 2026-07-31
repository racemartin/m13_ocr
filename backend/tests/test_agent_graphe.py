# ############################################################################
# Tests : graphe LangGraph de l'agent (app/application/agent/graphe_agent.py)
# ############################################################################
# Reutilise les memes fakes que test_explore.py / test_vector_search.py.
# Compile le graphe sans checkpointer (checkpointer=None) : aucun appel
# reseau ni binaire requis, comme pour les 11 tests pytest de l'Etape 2.

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
from   app.application.agent.graphe_agent import construire_graphe
from   app.domaine.modeles import CoupTheorique, Evaluation, ExtraitConnaissance
from   tests.conftest import FEN_POSITION_DEPART
from   tests.fakes import (
    FauxValidateurEchecs, FauxTheorieOuvertures, FauxMoteurEvaluation,
    FauxBaseConnaissances,
)


def construire_graphe_de_test(
    coups=None, evaluation=None, extraits=None, fen_valide=True,
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
    return construire_graphe(
        service_coups      = service_coups,
        service_evaluation = service_evaluation,
        service_contexte   = service_contexte,
        checkpointer        = None,
    )


def test_graphe_passe_par_le_contexte_quand_la_theorie_existe():
    coups = [CoupTheorique(uci="e2e4", san="e4", nombre_parties=125_000)]
    extraits = [
        ExtraitConnaissance(
            texte="...", ouverture="Sicilienne",
            source_url="https://fr.wikipedia.org/...", score=0.9,
        ),
    ]
    graphe = construire_graphe_de_test(coups=coups, extraits=extraits)

    resultat = graphe.invoke({"fen": FEN_POSITION_DEPART})

    assert resultat["coups_theoriques"] == coups
    assert "evaluation" not in resultat
    assert resultat["contexte_ouverture"] == extraits


def test_graphe_retombe_sur_stockfish_puis_contexte_si_aucune_theorie():
    evaluation = Evaluation(
        type="cp", valeur=39, coup_recommande="e2e4", profondeur=15,
    )
    graphe = construire_graphe_de_test(coups=[], evaluation=evaluation)

    resultat = graphe.invoke({"fen": FEN_POSITION_DEPART})

    assert resultat["coups_theoriques"] == []
    assert resultat["evaluation"] == evaluation
    assert resultat["contexte_ouverture"] == []


def test_graphe_fen_invalide_leve_value_error():
    graphe = construire_graphe_de_test(fen_valide=False)

    try:
        graphe.invoke({"fen": "ceci-nest-pas-un-fen-valide"})
        assert False, "ValueError attendue"
    except ValueError:
        pass
