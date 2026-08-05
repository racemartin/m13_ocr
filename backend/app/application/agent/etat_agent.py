# ############################################################################
# Etat partage du graphe LangGraph
# ############################################################################
# Cet etat ne fait que transiter des objets deja typees par le domaine
# (CoupTheorique, Evaluation, ExtraitConnaissance) ; aucune logique metier
# n'est portee ici. Chaque noeud du graphe lit et enrichit cet etat.
#
# NOTE : les dataclasses du domaine sont serialisables par le checkpointer
# LangGraph (serde ormsgpack, gere nativement les dataclasses). Aucune
# conversion manuelle en dict n'est donc necessaire ici ; la conversion
# vers un schema HTTP reste, elle, la responsabilite de app/api/v1/schemas.py.
#
# NOTE (version) : pyproject.toml fixe langgraph>=1.2.10 explicitement.
# Une version plus ancienne (observee : la resolution par defaut de
# "langgraph>=0.2.45") a montre un bug reproductible ou la mise a jour
# d'etat d'un noeud n'est pas vue par l'arete conditionnelle suivante ni
# par le resultat final -- confirme par un script de repro minimal,
# independant du reste du projet. Ne pas assouplir cette borne sans
# retester ce scenario precis (decision -> arete conditionnelle -> cle
# absente du resultat).

# Bibliotheque standard
from   typing import TypedDict    # Structure typee pour l'etat du graphe

# Modules internes
from   app.domaine.modeles import (    # Modeles du domaine
    CoupTheorique, Evaluation, ExtraitConnaissance, VideoExplicative,
)


class EtatAgent(TypedDict, total=False):
    """Etat transmis d'un noeud a l'autre du graphe de l'agent.

    `total=False` : chaque noeud ne renvoie que les cles qu'il modifie
    (convention LangGraph), le reste de l'etat est deja peuple par les
    noeuds precedents ou par l'appel initial.
    """

    fen                : str                        # Position a analyser
    id_session         : str                        # thread_id (Mongo)
    coups_theoriques   : list[CoupTheorique]        # Cf. /moves
    evaluation         : Evaluation                 # Cf. /evaluate
    contexte_ouverture : list[ExtraitConnaissance]  # Cf. /vector-search
                                                    # -------------------------
    rechercher_video   : bool                       # Decision du LLM
    requete_video      : str                        # Requete choisie par le LLM
    videos             : list[VideoExplicative]     # Resultat, si recherche faite
    explication        : str                        # Synthese pedagogique (LLM)