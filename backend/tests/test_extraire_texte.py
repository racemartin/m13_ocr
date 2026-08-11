# ############################################################################
# Tests : _extraire_texte -- normalisation reponse.content entre fournisseurs
# ############################################################################
# Regression guard pour le bug reel rencontre en production : Gemini
# renvoie reponse.content comme une LISTE de blocs, pas une chaine
# (contrairement a Anthropic), ce qui faisait planter la validation
# Pydantic de ReponseAgentLLM.explication avec un 500.

from app.application.agent.noeuds_agent_llm import _extraire_texte


def test_extraire_texte_avec_chaine_simple():
    """Format Anthropic : .content est deja une chaine."""
    assert _extraire_texte("Explication simple.") == "Explication simple."


def test_extraire_texte_avec_liste_de_blocs_gemini():
    """Format Gemini reel, reproduit depuis le bug de production."""
    contenu_gemini = [
        {"type": "text", "text": "Cette ouverture est theorique.",
         "extras": {"signature": "abc123"}},
    ]
    assert _extraire_texte(contenu_gemini) == "Cette ouverture est theorique."


def test_extraire_texte_avec_plusieurs_blocs():
    """Plusieurs blocs de texte doivent etre concatenes."""
    contenu = [
        {"type": "text", "text": "Premiere partie. "},
        {"type": "text", "text": "Deuxieme partie."},
    ]
    assert _extraire_texte(contenu) == "Premiere partie. Deuxieme partie."


def test_extraire_texte_avec_liste_de_chaines():
    """Cas limite : liste de chaines brutes, sans dict."""
    assert _extraire_texte(["Bonjour", " le monde"]) == "Bonjour le monde"


def test_extraire_texte_avec_bloc_sans_texte():
    """Un bloc sans cle 'text' (ex. bloc d'image) est ignore sans planter."""
    contenu = [
        {"type": "text", "text": "Visible."},
        {"type": "image", "data": "..."},
    ]
    assert _extraire_texte(contenu) == "Visible."
