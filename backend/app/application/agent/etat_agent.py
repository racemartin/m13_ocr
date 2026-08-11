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
# POINT DE VIGILANCE (confirme en conditions reelles) : LangGraph ignore
# SILENCIEUSEMENT toute cle renvoyee par un noeud si elle n'est pas
# declaree ici, dans EtatAgent -- aucune erreur, aucun warning. Un noeud
# peut tourner, calculer la bonne valeur, l'ecrire dans son log, et cette
# valeur disparait quand meme du resultat final si son champ manque dans
# ce TypedDict. Verifie : ce n'est PAS un bug de version de LangGraph
# (reproduit a l'identique sur langgraph==1.2.10 avec et sans le bug,
# selon que ce fichier declarait ou non les 4 champs ci-dessous). A
# chaque nouveau champ ajoute par un noeud (dans noeuds_agent.py ou
# noeuds_agent_llm.py), l'ajouter ICI EN PREMIER, avant d'ecrire le noeud.

# Bibliotheque standard
from   typing import TypedDict    # Structure typee pour l'etat du graphe

# Modules internes
from   app.domaine.modeles import (    # Modeles du domaine
    CoupTheorique, Evaluation, ExtraitConnaissance, InfoEco, VideoExplicative,
)


class EtatAgent(TypedDict, total=False):
    """Etat transmis d'un noeud a l'autre du graphe de l'agent.

    `total=False` : chaque noeud ne renvoie que les cles qu'il modifie
    (convention LangGraph), le reste de l'etat est deja peuple par les
    noeuds precedents ou par l'appel initial.
    """

    fen                : str                        # Position a analyser
    id_session         : str                        # thread_id (Mongo)
    eco                : InfoEco | None               # Code ECO identifie
    coups_theoriques   : list[CoupTheorique]         # Cf. /moves
    evaluation         : Evaluation                  # Cf. /evaluate
    contexte_ouverture : list[ExtraitConnaissance]    # Cf. /vector-search
    rechercher_video   : bool                        # Decision du LLM
    requete_video      : str                         # Requete choisie par le LLM
    videos             : list[VideoExplicative]       # Resultat, si recherche faite
    explication        : str                         # Synthese pedagogique (LLM)
