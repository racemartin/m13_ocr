# ############################################################################
# Script d'ingestion : Wikichess (URLs curées a la main dans le CSV)
# ############################################################################
# Lit ficgs_wikichess_aperturas.csv, scrape chaque page, et ecrit un JSON
# brut par entree dans backend/data/raw/wikichess/ -- meme structure que
# fetch_wikipedia.py (voir modele_brut.DonneeBrute).
#
# Tolerance aux pannes obligatoire : certaines pages Wikichess bloquent
# l'acces automatise de facon imprevisible (verifie manuellement -- meme
# schema d'URL, resultat different selon la page). Une page en echec ne
# doit jamais arreter le traitement des suivantes.

# Bibliotheque standard
import sys                          # Ajustement du chemin d'import
from   pathlib import Path          # Resolution des chemins absolus
import csv                          # Lecture du CSV curé
import re                           # Extraction par marqueurs structurels

# Racine du backend (scripts/ingestion/ -> scripts/ -> backend/), ajoutee
# au path AVANT l'import de "app" : ce script est autonome, hors du
# package applicatif, mais reutilise le meme outil de journalisation.
RACINE_BACKEND = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RACINE_BACKEND))

# Bibliotheques tierces
import httpx                        # Client HTTP
from   bs4 import BeautifulSoup     # Parsing HTML

# Modules internes
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree
from   modele_brut import DonneeBrute, ecrire_json_brut

log = LogTool(origin="fetch_wikichess")

DELAI_TIMEOUT_SECONDES = 10.0

# Certains sites servent une page reduite aux clients sans User-Agent de
# navigateur, meme avec un code 200 -- on se presente comme un navigateur
# courant pour eviter ce cas de figure.
ENTETES = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}


# ------------------------------------------------------------------------
# Extraction du texte narratif et des metadonnees d'une page Wikichess
# ------------------------------------------------------------------------
# NOTE : la page utilise <div align="justify"> comme style generique pour
# N'IMPORTE QUEL paragraphe justifie (menu, intro, footer...), pas comme
# marqueur unique du bloc qui nous interesse (confirme par l'inspecteur
# Chrome : "div:nth-child(20)", donc au moins 20 freres, pas un cas
# isole). On parcourt donc TOUS les divs candidats et on ne retient que
# celui qui contient reellement notre separateur fiable "====".
def extraire_contenu(html: str) -> dict | None:
    soupe = BeautifulSoup(html, "html.parser")
    candidats = soupe.find_all("div", attrs={"align": "justify"})

    conteneur = None
    for div in candidats:
        if "====" in div.get_text():
            conteneur = div
            break
    if conteneur is None:
        return None    # Aucun div candidat ne contient le bloc attendu

    texte_bloc = conteneur.get_text("\n")

    if "====" not in texte_bloc:
        return None    # Pas de separateur "====" -> uniquement des stats

    avant, _, apres = texte_bloc.partition("====")
    prose_avant = avant.strip()

    # Selon les pages, une partie de la prose narrative arrive APRES la
    # ligne "Contributors : ..." plutot qu'avant "====" (verifie sur des
    # pages reelles : ex. "1. a4", ou tout le texte utile suit la liste
    # des contributeurs). On l'extrait aussi, avant les balises [ECO ...].
    apres_contributeurs = re.sub(r"^.*?Contributors[^\n]*\n?", "", apres, flags=re.S)
    prose_apres = re.split(r'\[ECO "', apres_contributeurs)[0].strip()

    prose = "\n\n".join(p for p in (prose_avant, prose_apres) if p)
    if len(prose) < 15:
        return None    # Ni avant ni apres : page vraiment sans narration

    eco       = re.search(r'\[ECO "([^"]+)"\]', texte_bloc)
    ouverture = re.search(r'\[Opening "([^"]+)"\]', texte_bloc)
    variante  = re.search(r'\[Variation "([^"]+)"\]', texte_bloc)

    return {
        "prose"     : prose,
        "eco"       : eco.group(1) if eco else None,
        "opening"   : ouverture.group(1) if ouverture else None,
        "variation" : variante.group(1) if variante else None,
    }


# ------------------------------------------------------------------------
# Boucle principale : CSV -> scraping -> JSON brut
# ------------------------------------------------------------------------
def ingerer(chemin_csv: str, dossier_data: str) -> None:
    log.START_ACTION(
        "fetch_wikichess", "ingerer", "Scraping des URLs curées Wikichess",
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
                    url, headers=ENTETES, timeout=DELAI_TIMEOUT_SECONDES,
                )
                reponse.raise_for_status()
            except httpx.HTTPError as erreur:
                log.LEVEL_5_WARNING(
                    "fetch_wikichess", f"Echec pour {nom} ({url}) : {erreur}",
                )
                echouees += 1
                continue

            contenu = extraire_contenu(reponse.text)
            if contenu is None:
                # Sauvegarde le HTML brut pour inspection manuelle -- evite
                # de devoir deviner la cause d'un echec la prochaine fois.
                dossier_debug = Path(dossier_data) / "raw" / "_debug"
                dossier_debug.mkdir(parents=True, exist_ok=True)
                slug = re.sub(r"[^a-z0-9]+", "_", nom.lower()).strip("_")
                (dossier_debug / f"{slug}.html").write_text(
                    reponse.text, encoding="utf-8",
                )
                log.LEVEL_6_NOTICE(
                    "fetch_wikichess", f"Pas de prose exploitable pour {nom}",
                )
                echouees += 1
                continue

            donnee = DonneeBrute(
                source      = "wikichess",
                nom         = nom,
                categorie   = categorie,
                url         = url,
                langue      = "en",
                extrait     = contenu["prose"],
                metadonnees = {
                    "eco"       : contenu["eco"],
                    "opening"   : contenu["opening"],
                    "variation" : contenu["variation"],
                },
            )
            chemin = ecrire_json_brut(donnee, dossier_data)
            log.LEVEL_7_INFO("fetch_wikichess", f"Ecrit : {chemin}")
            reussies += 1

    log.PARAMETER_VALUE("reussies", reussies)
    log.PARAMETER_VALUE("echouees", echouees)
    log.FINISH_ACTION(
        "fetch_wikichess", "ingerer",
        f"{reussies} reussies, {echouees} echouees",
    )


if __name__ == "__main__":
    ingerer(
        chemin_csv   = str(RACINE_BACKEND / "data" / "seeds" / "ficgs_wikichess_aperturas.csv"),
        dossier_data = str(RACINE_BACKEND / "data"),
    )