#!/usr/bin/env python
# ############################################################################
# Script de test manuel de l'adaptateur YouTube (AdaptateurYoutube)
# ############################################################################
# A la difference de test_youtube_smoke.py (qui appelle googleapiclient
# directement, sans passer par le projet), ce script instancie le VRAI
# AdaptateurYoutube -- verifie donc que le mapping vers VideoExplicative,
# la construction de l'URL et le traitement des erreurs (quota, cle
# invalide) fonctionnent tels qu'ils tourneront reellement dans l'API.
#
# Complementaire de tests/test_videos.py (qui utilise FauxRechercheVideos,
# sans reseau) : ce script-ci consomme un peu de quota reel, a lancer donc
# ponctuellement, pas dans la suite pytest automatisee.
#
# Utilisation :
#   export YOUTUBE_API_KEY="ta_cle"
#   uv run python scripts/test_youtube_adapter.py
#   uv run python scripts/test_youtube_adapter.py --ouverture "Ruy Lopez"

import argparse
import os
import sys


from app.infrastructure.adaptateur_youtube import AdaptateurYoutube
from app.application.rechercher_videos_service import (
    RechercherVideosService,
)

# NOTE : ce script appelle AdaptateurYoutube directement, sans passer par
# app.core.dependances (c'est le but : tester l'adaptateur seul) -- donc
# il doit charger .env lui-meme, comme test_youtube_smoke.py.
from pathlib import Path
from dotenv import load_dotenv

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent  # ajustar segun profundidad
load_dotenv(RAIZ_REPO / ".env")


def afficher_resultat(nom: str, ok: bool, detail: str) -> None:
    etiquette = " OK " if ok else "ECHEC"
    print(f"[{etiquette}] {nom:<38} {detail}")


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--ouverture", default="Sicilienne",
        help="Nom d'ouverture a rechercher (defaut: Sicilienne)",
    )
    arguments = analyseur.parse_args()

    cle_api = os.environ.get("YOUTUBE_API_KEY")
    if not cle_api:
        print("Erreur : YOUTUBE_API_KEY absente de l'environnement.")
        return 1

    echecs = 0

    # ----------------------------------------------------------------
    # 1. L'adaptateur seul (couche infrastructure)
    # ----------------------------------------------------------------
    adaptateur = AdaptateurYoutube(cle_api=cle_api)
    videos = adaptateur.rechercher(
        f"{arguments.ouverture} chess opening tutorial explanation",
        max_resultats=5,
    )
    ok = len(videos) > 0
    echecs += 0 if ok else 1
    afficher_resultat(
        "AdaptateurYoutube.rechercher", ok,
        f"{len(videos)} video(s)" if ok else "0 video (verifie la cle/le quota)",
    )
    for v in videos[:3]:
        print(f"         - {v.titre}  [{v.chaine}]")
        print(f"           {v.url}")

    # ----------------------------------------------------------------
    # 2. Le service d'application au-dessus (requete "intelligente")
    # ----------------------------------------------------------------
    service = RechercherVideosService(recherche_videos=adaptateur)
    videos_service = service.executer(arguments.ouverture)
    ok = len(videos_service) > 0
    echecs += 0 if ok else 1
    afficher_resultat(
        "RechercherVideosService.executer", ok,
        f"{len(videos_service)} video(s) pour '{arguments.ouverture}'",
    )

    # ----------------------------------------------------------------
    # 3. Cas "aucun resultat" -- ne doit jamais lever d'exception
    # ----------------------------------------------------------------
    try:
        videos_absurdes = adaptateur.rechercher(
            "zzzzzzzzzzzzzzzz_requete_qui_ne_matchera_rien_9999",
        )
        ok = isinstance(videos_absurdes, list)
        afficher_resultat(
            "Gestion liste vide (pas d'exception)", ok,
            f"{len(videos_absurdes)} video(s), type={type(videos_absurdes).__name__}",
        )
    except Exception as erreur:
        echecs += 1
        afficher_resultat(
            "Gestion liste vide (pas d'exception)", False,
            f"A leve {type(erreur).__name__}: {erreur}",
        )

    print()
    print(f"Termine : {echecs} echec(s) sur 3 verifications.")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
