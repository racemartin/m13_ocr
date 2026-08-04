#!/usr/bin/env python
# ############################################################################
# Smoke-test de l'API YouTube Data v3 -- AUCUNE dependance au projet
# ############################################################################
# Le script le plus direct possible pour verifier que ta cle API et ton
# quota fonctionnent, avant meme d'ecrire le port/adaptateur. N'utilise ni
# LangGraph, ni FastAPI, ni le graphe de l'agent -- juste la cle et la
# bibliotheque officielle.
#
# Utilisation :
#   export YOUTUBE_API_KEY="ta_cle_ici"
#   uv run python scripts/test_youtube_smoke.py "Sicilienne chess opening"

import os
import sys

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# NOTE : ce script est autonome (n'importe pas app.core.dependances), donc
# il doit charger .env lui-meme -- sinon YOUTUBE_API_KEY reste invisible
# meme si le fichier existe sur disque.

from pathlib import Path
from dotenv import load_dotenv

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent  # ajustar segun profundidad
load_dotenv(RAIZ_REPO / ".env")


def main() -> int:
    cle = os.environ.get("YOUTUBE_API_KEY")
    if not cle:
        print("Erreur : variable d'environnement YOUTUBE_API_KEY absente.")
        return 1

    requete = sys.argv[1] if len(sys.argv) > 1 else "Sicilian defense chess opening"

    client = build("youtube", "v3", developerKey=cle)

    try:
        reponse = client.search().list(
            q=requete,
            part="snippet",
            type="video",
            maxResults=5,
        ).execute()
    except HttpError as erreur:
        print(f"Echec de l'appel API : {erreur}")
        if erreur.resp.status == 403:
            print("(403 = tres probablement quota journalier depasse, "
                  "ou cle API mal configuree/restreinte)")
        return 1
    except Exception as erreur:
        print(f"Echec reseau ({type(erreur).__name__}) : {erreur}")
        print("(si tu es sur un reseau d'entreprise avec proxy/inspection "
              "SSL, c'est le suspect le plus probable -- verifie aupres "
              "de ton service IT si un certificat racine doit etre "
              "installe/configure pour Python)")
        return 1

    elements = reponse.get("items", [])
    print(f"{len(elements)} resultat(s) pour : {requete!r}\n")
    for item in elements:
        video_id = item["id"]["videoId"]
        titre    = item["snippet"]["title"]
        chaine   = item["snippet"]["channelTitle"]
        print(f"  - {titre}  [{chaine}]")
        print(f"    https://www.youtube.com/watch?v={video_id}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
