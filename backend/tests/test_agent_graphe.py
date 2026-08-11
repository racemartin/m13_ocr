# ############################################################################
# Tests : graphe LangGraph de l'agent (app/application/agent/graphe_agent.py)
# ############################################################################
# Reutilise les memes fakes que test_explore.py / test_vector_search.py.
# Compile le graphe sans checkpointer (checkpointer=None) : aucun appel
# reseau ni binaire requis, comme pour les 11 tests pytest de l'Etape 2.
#
# NOTE : couvre uniquement la version de BASE du graphe (sans LLM). Les
# tests de la variante LLM (decision video + synthese) vivent a part,
# dans test_agent_graphe_llm.py.

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
from   app.application.identifier_eco_service import (      # Cas
    IdentifierEcoService,                                    # d'usage
)
from   app.application.agent.graphe_agent import construire_graphe
from   app.domaine.modeles import (
    CoupTheorique, Evaluation, ExtraitConnaissance, InfoEco,
)
from   tests.conftest import FEN_POSITION_DEPART
from   tests.fakes import (
    FauxValidateurEchecs, FauxTheorieOuvertures, FauxMoteurEvaluation,
    FauxBaseConnaissances, FauxIdentificationEco,
)


def construire_graphe_de_test(
    coups=None, evaluation=None, extraits=None, fen_valide=True, eco=None,
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
    service_eco = IdentifierEcoService(
        identification_eco = FauxIdentificationEco(resultat=eco),
    )
    graphe = construire_graphe(
        service_coups      = service_coups,
        service_evaluation = service_evaluation,
        service_contexte   = service_contexte,
        service_eco         = service_eco,
        checkpointer          = None,
    )
    # Retourne aussi le fake Milvus : permet de verifier QUELLE requete
    # a ete envoyee (ex. nom d'ouverture vs FEN brut, cf. l'amelioration
    # liee a l'identification ECO).
    return graphe, service_contexte.base_connaissances


def test_graphe_passe_par_le_contexte_quand_la_theorie_existe():
    coups = [CoupTheorique(uci="e2e4", san="e4", nombre_parties=125_000)]
    extraits = [
        ExtraitConnaissance(
            texte="...", ouverture="Sicilienne",
            source_url="https://fr.wikipedia.org/...", score=0.9,
        ),
    ]
    graphe, _ = construire_graphe_de_test(coups=coups, extraits=extraits)

    resultat = graphe.invoke({"fen": FEN_POSITION_DEPART})

    assert resultat["coups_theoriques"] == coups
    assert "evaluation" not in resultat
    assert resultat["contexte_ouverture"] == extraits


def test_graphe_retombe_sur_stockfish_puis_contexte_si_aucune_theorie():
    evaluation = Evaluation(
        type="cp", valeur=39, coup_recommande="e2e4", profondeur=15,
    )
    graphe, _ = construire_graphe_de_test(coups=[], evaluation=evaluation)

    resultat = graphe.invoke({"fen": FEN_POSITION_DEPART})

    assert resultat["coups_theoriques"] == []
    assert resultat["evaluation"] == evaluation
    assert resultat["contexte_ouverture"] == []


def test_graphe_fen_invalide_leve_value_error():
    graphe, _ = construire_graphe_de_test(fen_valide=False)

    try:
        graphe.invoke({"fen": "ceci-nest-pas-un-fen-valide"})
        assert False, "ValueError attendue"
    except ValueError:
        pass


def test_graphe_identifie_eco_et_ameliore_la_requete_rag():
    """Verifie les 2 effets de l'identification ECO :
    1. le champ 'eco' est bien renvoye dans l'etat final ;
    2. la requete envoyee au RAG utilise le nom de la famille
       d'ouverture, PAS le FEN brut (amelioration liee a l'ECO)."""
    eco = InfoEco(
        code="B20", nom="Sicilian Defense", famille="Sicilian Defense",
        categorie="Jeux semi-ouverts (hors Francaise)",
    )
    coups = [CoupTheorique(uci="e2e4", san="e4", nombre_parties=125_000)]

    graphe, fausse_base = construire_graphe_de_test(coups=coups, eco=eco)

    resultat = graphe.invoke({"fen": FEN_POSITION_DEPART})

    assert resultat["eco"] == eco
    assert fausse_base.derniere_requete == "Sicilian Defense"
    assert fausse_base.derniere_requete != FEN_POSITION_DEPART


def test_graphe_repli_sur_fen_brut_si_eco_non_trouve():
    """Position non cataloguee (eco=None) : la requete RAG retombe sur
    le FEN brut, comportement d'avant l'ajout de l'identification ECO."""
    graphe, fausse_base = construire_graphe_de_test(coups=[], eco=None)

    resultat = graphe.invoke({"fen": FEN_POSITION_DEPART})

    assert resultat["eco"] is None
    assert fausse_base.derniere_requete == FEN_POSITION_DEPART
