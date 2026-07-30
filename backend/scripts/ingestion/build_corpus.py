# ############################################################################
# Script de normalisation : data/raw/*/*.json -> data/corpus/*.md
# ############################################################################
# Seul script qui lit les deux sources ensemble -- et il ne sait rien de
# leurs differences, grace au schema commun DonneeBrute (modele_brut.py).
# Un fichier .md par article JSON, meme granularite de bout en bout.

# Bibliotheque standard
import sys                # Ajustement du chemin d'import
from   pathlib import Path
import json                # Lecture des JSON bruts

RACINE_BACKEND = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RACINE_BACKEND))

# Modules internes
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="build_corpus")


# ------------------------------------------------------------------------
# Construit le frontmatter YAML + corps d'un document .md normalise
# ------------------------------------------------------------------------
def construire_markdown(donnee: dict) -> str:
    lignes_frontmatter = [
        "---",
        f"source: {donnee['source']}",
        f"nom: {donnee['nom']}",
        f"categorie: {donnee['categorie']}",
        f"url: {donnee['url']}",
        f"langue: {donnee['langue']}",
    ]
    for cle, valeur in donnee.get("metadonnees", {}).items():
        if valeur:
            lignes_frontmatter.append(f"{cle}: {valeur}")
    lignes_frontmatter.append("---")

    return "\n".join(lignes_frontmatter) + "\n\n" + donnee["extrait"] + "\n"


# ------------------------------------------------------------------------
# Boucle principale : parcourt data/raw/*/*.json -> ecrit data/corpus/*.md
# ------------------------------------------------------------------------
def construire_corpus(dossier_raw: str, dossier_corpus: str) -> None:
    log.START_ACTION(
        "build_corpus", "construire_corpus",
        "Normalisation des JSON bruts en corpus .md",
    )

    dossier_raw    = Path(dossier_raw)
    dossier_corpus = Path(dossier_corpus)
    dossier_corpus.mkdir(parents=True, exist_ok=True)

    fichiers_json = sorted(dossier_raw.glob("*/*.json"))
    log.PARAMETER_VALUE("nombre_fichiers_json", len(fichiers_json))

    reussies, echouees = 0, 0
    for chemin_json in fichiers_json:
        try:
            donnee = json.loads(chemin_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as erreur:
            log.LEVEL_5_WARNING(
                "build_corpus", f"JSON invalide : {chemin_json} ({erreur})",
            )
            echouees += 1
            continue

        champs_requis = {"source", "nom", "categorie", "url", "langue", "extrait"}
        if not champs_requis.issubset(donnee):
            log.LEVEL_5_WARNING(
                "build_corpus", f"Champs manquants dans {chemin_json}",
            )
            echouees += 1
            continue

        markdown    = construire_markdown(donnee)
        nom_fichier = chemin_json.stem + ".md"
        chemin_md   = dossier_corpus / nom_fichier
        chemin_md.write_text(markdown, encoding="utf-8")
        reussies += 1

    log.PARAMETER_VALUE("reussies", reussies)
    log.PARAMETER_VALUE("echouees", echouees)
    log.FINISH_ACTION(
        "build_corpus", "construire_corpus",
        f"{reussies} fichiers .md, {echouees} ignores",
    )


if __name__ == "__main__":
    construire_corpus(
        dossier_raw    = str(RACINE_BACKEND / "data" / "raw"),
        dossier_corpus = str(RACINE_BACKEND / "data" / "corpus"),
    )
