# ############################################################################
# Modele commun des donnees brutes (raw JSON)
# ############################################################################
# Les deux scripts de fetch (wikichess, wikipedia) DOIVENT ecrire des
# fichiers JSON respectant exactement cette meme structure, quelle que
# soit la source. C'est ce qui permettra, plus tard, a un unique script
# de normalisation (build_documents.py) de lire data/raw/*/*.json sans
# jamais avoir a savoir d'ou vient chaque fichier.

# Bibliotheque standard
import json                          # Serialisation
from   dataclasses import dataclass, asdict, field
from   datetime import datetime, timezone
from   pathlib import Path


# ------------------------------------------------------------------------
# Structure UNIQUE pour toute donnee brute recuperee, quelle que soit
# la source (wikichess ou wikipedia)
# ------------------------------------------------------------------------
@dataclass
class DonneeBrute:
    source     : str                  # "wikichess" | "wikipedia"
    nom        : str                  # Nom lisible de l'ouverture/article
    categorie  : str                  # Colonne "categoria" du CSV curé
    url        : str                  # URL d'origine
    langue     : str                  # "fr" | "en"
    extrait    : str                  # Texte de prose (ce qui sera vectorise)
    metadonnees: dict = field(default_factory=dict)   # Specifique a la
                                                        # source (eco, opening...)
    recupere_le: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )


# ------------------------------------------------------------------------
# Ecriture normalisee : meme nom de fichier, meme format, pour les 2 sources
# ------------------------------------------------------------------------
def ecrire_json_brut(donnee: DonneeBrute, dossier_racine: str) -> Path:
    dossier = Path(dossier_racine) / "raw" / donnee.source
    dossier.mkdir(parents=True, exist_ok=True)

    slug = (
        donnee.nom.lower()
        .replace(" ", "_")
        .replace("'", "")
        .replace("’", "")
    )
    slug = "".join(c for c in slug if c.isalnum() or c == "_")

    chemin = dossier / f"{donnee.source}_{slug}.json"
    chemin.write_text(
        json.dumps(asdict(donnee), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return chemin
