# ############################################################################
# Tests : adaptateur ECO (index precalcule, dataset lichess-org)
# ############################################################################
# Comme pour Polyglot, ce test lit le vrai fichier index_eco.json --
# integration legere, sans reseau ni service externe.

# Bibliotheques tierces
import chess

# Modules internes
from   app.infrastructure.adaptateur_eco import AdaptateurEco

CHEMIN_INDEX_TEST = "data/eco/index_eco.json"


def test_eco_categorie_derivee_de_la_lettre():
    """Verifie la classification standard sur plusieurs lettres, pas
    seulement B -- ex. C60 (Ruy Lopez) et D06 (Gambit Dame)."""
    adaptateur = AdaptateurEco(chemin_index=CHEMIN_INDEX_TEST)

    plateau_c60 = chess.Board()
    for coup_san in ["e4", "e5", "Nf3", "Nc6", "Bb5"]:
        plateau_c60.push_san(coup_san)
    resultat_c60 = adaptateur.identifier(plateau_c60.fen())
    assert resultat_c60.categorie == "Jeux ouverts et Defense Francaise"

    plateau_d06 = chess.Board()
    for coup_san in ["d4", "d5", "c4"]:
        plateau_d06.push_san(coup_san)
    resultat_d06 = adaptateur.identifier(plateau_d06.fen())
    assert resultat_d06.categorie == "Jeux fermes et semi-fermes"


def test_eco_identifie_la_sicilienne():
    adaptateur = AdaptateurEco(chemin_index=CHEMIN_INDEX_TEST)

    # 1.e4 c5 -- Defense sicilienne (ligne generique, pas encore une
    # variante nommee -- famille et nom sont donc identiques ici)
    fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"

    resultat = adaptateur.identifier(fen)

    assert resultat is not None
    assert resultat.code == "B20"
    assert "Sicilian" in resultat.nom
    assert resultat.famille == "Sicilian Defense"
    assert resultat.categorie == "Jeux semi-ouverts (hors Francaise)"


def test_eco_separe_famille_et_variante_najdorf():
    """1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6 -- Najdorf, B90.
    Verifie que famille != nom complet des qu'une variante est nommee."""
    adaptateur = AdaptateurEco(chemin_index=CHEMIN_INDEX_TEST)

    plateau = chess.Board()
    for coup_san in ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "a6"]:
        plateau.push_san(coup_san)

    resultat = adaptateur.identifier(plateau.fen())

    assert resultat is not None
    assert resultat.code == "B90"
    assert resultat.famille == "Sicilian Defense"
    assert resultat.nom == "Sicilian Defense: Najdorf Variation"
    assert resultat.famille != resultat.nom


def test_eco_ignore_les_compteurs_de_coups():
    """Deux FEN ne differant que par les compteurs halfmove/fullmove
    doivent renvoyer le meme resultat -- ils ne changent pas l'identite
    de l'ouverture."""
    adaptateur = AdaptateurEco(chemin_index=CHEMIN_INDEX_TEST)

    fen_a = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    fen_b = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 5 12"

    assert adaptateur.identifier(fen_a) == adaptateur.identifier(fen_b)


def test_eco_retourne_none_pour_position_non_cataloguee():
    adaptateur = AdaptateurEco(chemin_index=CHEMIN_INDEX_TEST)

    fen_absurde = "8/8/8/8/8/8/8/8 w - - 0 1"    # Plateau vide, jamais atteignable

    assert adaptateur.identifier(fen_absurde) is None
