# ############################################################################
# Script de diagnostic : affiche le contenu brut recu pour LA PREMIERE URL
# ############################################################################
# Objectif unique : voir exactement ce que le serveur renvoie, sans aucune
# extraction ni logique -- pour savoir si c'est bien la page Wikichess
# attendue, une redirection, une page de blocage, etc.

import csv
from   pathlib import Path

import httpx

ENTETES = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}

racine_backend = Path(__file__).resolve().parent.parent.parent
chemin_csv = racine_backend / "data" / "seeds" / "ficgs_wikichess_aperturas.csv"

with open(chemin_csv, encoding="utf-8") as fichier:
    premiere_ligne = next(csv.DictReader(fichier))

url = premiere_ligne["url"]
print(f"URL testee : {url}\n")

reponse = httpx.get(url, headers=ENTETES, timeout=10.0)

print("Status code   :", reponse.status_code)
print("Content-Type  :", reponse.headers.get("content-type"))
print("URL finale    :", reponse.url, "(apres redirections eventuelles)")
print("Longueur texte:", len(reponse.text), "caracteres")
print()
print("--- 1500 premiers caracteres du contenu recu ---")
print(reponse.text[:1500])
