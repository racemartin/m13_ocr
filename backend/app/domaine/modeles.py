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
