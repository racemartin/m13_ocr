# ############################################################################
# Adaptateur d'infrastructure : theorie des ouvertures via un livre Polyglot
# ############################################################################
# Sert de source de repli (fallback) locale a l'adaptateur Lichess : ne
# depend d'aucun service externe, donc jamais indisponible.
#
# ATTENTION au sens du champ "nombre_parties" ici : un livre Polyglot ne
# contient pas de statistiques de parties reelles, seulement un "poids"
# (weight) exprimant la preference du livre pour ce coup. On reutilise le
# meme champ du modele de domaine par simplicite, mais ce n'est PAS un
# nombre de parties comme celui fourni par l'adaptateur Lichess.

# Bibliotheques tierces
import chess               # Regles du jeu d'echecs (deja une dependance)
import chess.polyglot as polyglot    # Lecture de livres Polyglot (.bin)

# Modules internes
from   app.domaine.modeles import CoupTheorique                # Modele
from   app.domaine.ports.port_theorie_ouvertures import (      # Port a
    PortTheorieOuvertures,                                     # implementer
)
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="adaptateur_polyglot")


class AdaptateurPolyglot(PortTheorieOuvertures):
    def __init__(self, chemin_livre: str) -> None:
        self.chemin_livre = chemin_livre

    # ------------------------------------------------------------------
    # Lecture du livre local (aucun appel reseau, jamais indisponible)
    # ------------------------------------------------------------------
    def coups_theoriques(self, fen: str) -> list[CoupTheorique]:
        log.START_ACTION(
            "AdaptateurPolyglot", "coups_theoriques",
            "Lecture du livre d'ouvertures local",
        )
        log.PARAMETER_VALUE("fen", fen)
        log.PARAMETER_VALUE("chemin_livre", self.chemin_livre)

        plateau = chess.Board(fen)

        try:
            with polyglot.open_reader(self.chemin_livre) as livre:
                entrees = list(livre.find_all(plateau))
        except (OSError, IndexError) as erreur:
            log.LEVEL_5_WARNING(
                "AdaptateurPolyglot", f"Livre Polyglot illisible : {erreur}",
            )
            log.FINISH_ACTION(
                "AdaptateurPolyglot", "coups_theoriques", "Livre illisible",
            )
            return []

        coups = [
            CoupTheorique(
                uci            = entree.move.uci(),
                san            = plateau.san(entree.move),
                # NOTE : poids du livre, pas un nombre de parties reelles
                nombre_parties = entree.weight,
            )
            for entree in entrees
        ]

        log.PARAMETER_VALUE("nombre_coups_trouves", len(coups))
        log.FINISH_ACTION(
            "AdaptateurPolyglot", "coups_theoriques",
            f"{len(coups)} coup(s) trouve(s) dans le livre",
        )
        return coups
