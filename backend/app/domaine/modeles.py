# ############################################################################
# Modeles du domaine
# ############################################################################
# Structures de donnees pures, sans aucune dependance vers un framework, une
# bibliotheque d'echecs ou un client HTTP. Elles representent les concepts
# metier manipules par les cas d'utilisation (couche application).

# Bibliotheque standard
from   dataclasses import dataclass    # Structures de donnees immuables


# ------------------------------------------------------------------------
# Un coup theorique connu de la base d'ouvertures (Lichess)
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class CoupTheorique:
    uci             : str    # Notation machine, ex. "e2e4"
    san             : str    # Notation lisible, ex. "e4"
    nombre_parties  : int    # Nombre de parties jouees avec ce coup


# ------------------------------------------------------------------------
# Evaluation d'une position par un moteur d'echecs (Stockfish)
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class Evaluation:
    type            : str          # "cp" (centipawns) ou "mate" (mat en N)
    valeur          : int          # Valeur associee au type
    coup_recommande : str | None = None    # Meilleur coup, notation UCI
    profondeur      : int         = 0      # Profondeur de recherche utilisee


# ------------------------------------------------------------------------
# Resultat combine de l'exploration d'une position (theorie ou moteur)
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultatExploration:
    type       : str                             # "theorie" ou "evaluation"
    coups      : list[CoupTheorique] | None = None
    evaluation : Evaluation          | None = None


# ------------------------------------------------------------------------
# Extrait de connaissance retrouve par recherche vectorielle (RAG, Milvus)
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class ExtraitConnaissance:
    texte      : str    # Contenu textuel de l'extrait
    ouverture  : str    # Nom de l'ouverture concernee
    source_url : str    # URL de la source d'origine (Wikipedia, Wikichess)
    score      : float  # Score de similarite (plus haut = plus pertinent)


# ------------------------------------------------------------------------
# Video explicative trouvee via l'API YouTube Data v3
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class VideoExplicative:
    id_video  : str        # Identifiant YouTube, ex. "dQw4w9WgXcQ"
    titre     : str        # Titre de la video
    chaine    : str        # Nom de la chaine qui l'a publiee
    url       : str        # URL complete, prete a afficher/ouvrir
    vues      : int = 0    # Nombre de vues (signal de qualite, cf. filtre)


# ------------------------------------------------------------------------
# Identification ECO d'une position (Encyclopedia of Chess Openings)
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class InfoEco:
    code      : str    # Code ECO, ex. "B90"
    nom       : str    # Nom complet, ex. "Sicilian Defense: Najdorf Variation"
    famille   : str    # Famille seule, ex. "Sicilian Defense"
    categorie : str    # Categorie ECO (A-E), ex. "Jeux semi-ouverts"
