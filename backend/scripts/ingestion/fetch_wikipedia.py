# ############################################################################
# Script d'ingestion : Wikipedia FR (URLs curées a la main dans le CSV)
# ############################################################################
# Lit ouverture_echecs_wikipedia.csv, appelle l'API REST officielle, et
# ecrit un JSON brut par entree dans backend/data/raw/wikipedia/ -- meme
# structure que fetch_wikichess.py (voir modele_brut.DonneeBrute).

# Bibliotheque standard
import sys                          # Ajustement du chemin d'import
from   pathlib import Path          # Resolution des chemins absolus
import csv                          # Lecture du CSV curé
from   urllib.parse import urlparse # Extraction du titre depuis l'URL

RACINE_BACKEND = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RACINE_BACKEND))

# Bibliotheques tierces
import httpx    # Client HTTP

# Modules internes
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree
from   modele_brut import DonneeBrute, ecrire_json_brut

log = LogTool(origin="fetch_wikipedia")

URL_RESUME = "https://fr.wikipedia.org/api/rest_v1/page/summary"
DELAI_TIMEOUT_SECONDES = 10.0

# La politique d'usage de l'API Wikimedia (etiquette API) exige un
# User-Agent descriptif, identifiant l'application et un contact.
# Sans cela, les requetes sont bloquees avec 403 Forbidden -- confirme
# en pratique : 165/165 echecs avec le User-Agent par defaut de httpx.
# Reference : https://meta.wikimedia.org/wiki/User-Agent_policy
ENTETES = {
    "User-Agent": (
        "FFE-Chess-Agent/0.1 "
        "(POC Federation Francaise des Echecs ; "
        "usage educatif OpenClassrooms ; contact: rafael@example.com)"
    ),
}


# ------------------------------------------------------------------------
# Extrait le titre d'article (deja URL-encode) depuis une URL Wikipedia
# ------------------------------------------------------------------------
def extraire_titre(url: str) -> str:
    return urlparse(url).path.split("/wiki/")[-1]


# ------------------------------------------------------------------------
# Boucle principale : CSV -> API REST -> JSON brut
# ------------------------------------------------------------------------
def ingerer(chemin_csv: str, dossier_data: str) -> None:
    log.START_ACTION(
        "fetch_wikipedia", "ingerer", "Appel API REST Wikipedia FR",
    )
    log.PARAMETER_VALUE("chemin_csv", chemin_csv)

    reussies, echouees = 0, 0

    with open(chemin_csv, encoding="utf-8") as fichier:
        for ligne in csv.DictReader(fichier):
            nom, categorie, url = (
                ligne["nombre_apertura"], ligne["categoria"], ligne["url"],
            )
            try:
                reponse = httpx.get(
                    f"{URL_RESUME}/{extraire_titre(url)}",
                    headers=ENTETES,
                    timeout=DELAI_TIMEOUT_SECONDES,
                )
                reponse.raise_for_status()
            except httpx.HTTPError as erreur:
                log.LEVEL_5_WARNING(
                    "fetch_wikipedia", f"Echec pour {nom} ({url}) : {erreur}",
                )
                echouees += 1
                continue

            resume = reponse.json()
            if "extract" not in resume or not resume["extract"]:
                log.LEVEL_6_NOTICE(
                    "fetch_wikipedia", f"Pas d'extrait exploitable pour {nom}",
                )
                echouees += 1
                continue

            donnee = DonneeBrute(
                source      = "wikipedia",
                nom         = nom,
                categorie   = categorie,
                url         = url,
                langue      = "fr",
                extrait     = resume["extract"],
                metadonnees = {},
            )
            chemin = ecrire_json_brut(donnee, dossier_data)
            log.LEVEL_7_INFO("fetch_wikipedia", f"Ecrit : {chemin}")
            reussies += 1

    log.PARAMETER_VALUE("reussies", reussies)
    log.PARAMETER_VALUE("echouees", echouees)
    log.FINISH_ACTION(
        "fetch_wikipedia", "ingerer",
        f"{reussies} reussies, {echouees} echouees",
    )


if __name__ == "__main__":
    ingerer(
        chemin_csv   = str(RACINE_BACKEND / "data" / "seeds" / "ouverture_echecs_wikipedia.csv"),
        dossier_data = str(RACINE_BACKEND / "data"),
    )