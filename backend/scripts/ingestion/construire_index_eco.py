#!/usr/bin/env python
# ############################################################################
# Construit l'index FEN -> {eco, nom} a partir du dataset ouvert
# lichess-org/chess-openings (MIT), en rejouant chaque ligne avec
# python-chess. Ecrit data/eco/index_eco.json (lu par AdaptateurEco).
# ############################################################################
# Le dataset ne fournit que la sequence de coups (PGN), pas de FEN -- ce
# script rejoue chaque ligne UNE FOIS a la construction, pour obtenir une
# recherche en O(1) au moment de la requete (meme logique que le livre
# Polyglot : precalcul offline, lecture rapide en ligne).
#
# La FEN est normalisee en ignorant les compteurs de demi-coups/coups
# complets : ils ne changent pas l'identite de l'ouverture.
#
# Utilisation :
#   uv run python scripts/ingestion/construire_index_eco.py

# Bibliotheque standard
import sys                          # Ajustement du chemin d'import
from   pathlib import Path          # Resolution des chemins absolus
import csv                          # Lecture des TSV sources
import io                           # Lecture du PGN en memoire
import json                         # Ecriture de l'index final

RACINE_BACKEND = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RACINE_BACKEND))

# Bibliotheques tierces
import httpx    # Telechargement des TSV sources
import chess          # Regles du jeu d'echecs
import chess.pgn      # Lecture de sequences PGN

# Modules internes
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="construire_index_eco")

URL_BASE = "https://raw.githubusercontent.com/lichess-org/chess-openings/master"
FICHIERS = ["a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv"]
DOSSIER_SORTIE = RACINE_BACKEND / "data" / "eco"


def normaliser_fen(fen_complete: str) -> str:
    """Garde uniquement : position, trait, roques, prise en passant."""
    return " ".join(fen_complete.split(" ")[:4])


def telecharger_tsv(nom_fichier: str) -> str:
    log.START_ACTION("construire_index_eco", "telecharger_tsv", nom_fichier)
    reponse = httpx.get(f"{URL_BASE}/{nom_fichier}", timeout=30.0)
    reponse.raise_for_status()
    log.FINISH_ACTION(
        "construire_index_eco", "telecharger_tsv",
        f"{len(reponse.text.splitlines())} ligne(s)",
    )
    return reponse.text


def construire_index() -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    lignes_ok = 0
    lignes_erreur = 0

    for nom_fichier in FICHIERS:
        contenu_tsv = telecharger_tsv(nom_fichier)
        lecteur = csv.DictReader(io.StringIO(contenu_tsv), delimiter="\t")

        for ligne in lecteur:
            eco = ligne["eco"]
            nom = ligne["name"]
            pgn = ligne["pgn"]

            try:
                plateau = chess.Board()
                partie = chess.pgn.read_game(io.StringIO(pgn))
                for coup in partie.mainline_moves():
                    plateau.push(coup)

                fen_normalisee = normaliser_fen(plateau.fen())

                # Transposition (2 lignes -> meme position) : on garde la
                # PREMIERE rencontree (ordre a..e = ordre ECO standard).
                if fen_normalisee not in index:
                    index[fen_normalisee] = {"eco": eco, "nom": nom}
                lignes_ok += 1

            except Exception as erreur:
                lignes_erreur += 1
                log.LEVEL_6_NOTICE(
                    "construire_index_eco",
                    f"Ligne ignoree ({eco} {nom!r}) : {erreur}",
                )

    log.LEVEL_7_INFO(
        "construire_index_eco",
        f"{lignes_ok} ligne(s) indexee(s), {lignes_erreur} ignoree(s), "
        f"{len(index)} position(s) unique(s)",
    )
    return index


if __name__ == "__main__":
    log.START_ACTION(
        "construire_index_eco", "main",
        "Construction de l'index ECO (lichess-org/chess-openings)",
    )

    index = construire_index()

    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    chemin_sortie = DOSSIER_SORTIE / "index_eco.json"
    with open(chemin_sortie, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)

    log.FINISH_ACTION(
        "construire_index_eco", "main",
        f"Ecrit : {chemin_sortie} "
        f"({chemin_sortie.stat().st_size / 1024:.0f} Ko)",
    )
