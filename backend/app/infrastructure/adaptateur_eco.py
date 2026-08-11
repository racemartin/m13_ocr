# ############################################################################
# Adaptateur d'infrastructure : identification ECO via un index precalcule
# ############################################################################
# L'index (data/eco/index_eco.json) est construit UNE FOIS, hors-ligne, par
# scripts/ingestion/construire_index_eco.py, a partir du dataset ouvert
# lichess-org/chess-openings (3810 lignes theoriques). Cet adaptateur ne
# fait qu'une lecture directe dans un dict deja en memoire -- O(1), aucun
# appel reseau, aucune dependance a un service externe.
#
# La FEN est normalisee (position + trait + roques + prise en passant
# uniquement, sans les compteurs de demi-coups/coups complets) car ces
# compteurs ne changent pas l'identite d'une ouverture -- seul le chemin
# pour y arriver differe.

# Bibliotheque standard
import json    # Lecture de l'index precalcule

# Modules internes
from   app.domaine.modeles import InfoEco                          # Modele
from   app.domaine.ports.port_identification_eco import (          # Port a
    PortIdentificationEco,                                         # implementer
)
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="adaptateur_eco")

# Classification standard ECO (Encyclopedia of Chess Openings), constante,
# derivee de la seule premiere lettre du code -- aucun dataset requis.
# Verifiee independamment aupres de plusieurs sources (chessprogramming.org,
# Wikipedia, l'Informator original).
CATEGORIES_ECO: dict[str, str] = {
    "A": "Jeux de flanc",
    "B": "Jeux semi-ouverts (hors Francaise)",
    "C": "Jeux ouverts et Defense Francaise",
    "D": "Jeux fermes et semi-fermes",
    "E": "Defenses indiennes",
}


class AdaptateurEco(PortIdentificationEco):
    def __init__(self, chemin_index: str) -> None:
        self.chemin_index = chemin_index

        log.START_ACTION("AdaptateurEco", "__init__", "Chargement de l'index ECO")
        log.PARAMETER_VALUE("chemin_index", chemin_index)

        with open(chemin_index, encoding="utf-8") as f:
            self._index: dict[str, dict[str, str]] = json.load(f)

        log.FINISH_ACTION(
            "AdaptateurEco", "__init__",
            f"{len(self._index)} position(s) chargee(s)",
        )

    def identifier(self, fen: str) -> InfoEco | None:
        fen_normalisee = self._normaliser_fen(fen)
        entree = self._index.get(fen_normalisee)

        if entree is None:
            return None

        try:
            return InfoEco(
                code=entree["eco"],
                nom=entree["nom"],
                famille=entree["famille"],
                categorie=CATEGORIES_ECO.get(entree["eco"][0], "Categorie inconnue"),
            )
        except KeyError as champ_manquant:
            raise RuntimeError(
                f"index_eco.json desynchronise avec le code : champ "
                f"{champ_manquant} absent. Reconstruire l'index avec "
                f"scripts/ingestion/construire_index_eco.py, ou verifier "
                f"que le bon fichier a bien ete copie dans data/eco/."
            ) from champ_manquant

    @staticmethod
    def _normaliser_fen(fen: str) -> str:
        morceaux = fen.split(" ")
        return " ".join(morceaux[:4])
