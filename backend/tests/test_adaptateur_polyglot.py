# ############################################################################
# Tests : adaptateur Polyglot (livre local de secours)
# ############################################################################
# Contrairement aux tests des endpoints (qui utilisent des fakes), ce
# test lit le vrai fichier .bin : c'est un test d'integration leger,
# volontairement isole, qui ne depend d'aucun reseau ni service externe.

# Modules internes
from   app.infrastructure.adaptateur_polyglot import AdaptateurPolyglot
from   tests.conftest import FEN_POSITION_DEPART

CHEMIN_LIVRE_TEST = "data/polyglot/livre_ouvertures.bin"


def test_polyglot_retourne_des_coups_depuis_la_position_de_depart():
    adaptateur = AdaptateurPolyglot(chemin_livre=CHEMIN_LIVRE_TEST)

    coups = adaptateur.coups_theoriques(FEN_POSITION_DEPART)

    assert len(coups) > 0
    ucis = {coup.uci for coup in coups}
    assert "e2e4" in ucis


def test_polyglot_retourne_liste_vide_si_livre_introuvable():
    adaptateur = AdaptateurPolyglot(chemin_livre="chemin/inexistant.bin")

    coups = adaptateur.coups_theoriques(FEN_POSITION_DEPART)

    assert coups == []
