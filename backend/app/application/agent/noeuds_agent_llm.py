# ############################################################################
# Noeuds du graphe -- variante LLM (decision + execution associee)
# ############################################################################
# Separes de noeuds_agent.py a dessein : ce fichier regroupe tout ce qui
# n'existe QUE dans le graphe LLM (graphe_agent_llm.py). Utile pour
# l'audit (cout, latence, points de defaillance) -- quiconque cherche
# "ou appelle-t-on un LLM dans l'agent ?" sait que c'est ici, et nulle
# part ailleurs.
#
# Discipline hexagonale : seuls fabriquer_noeud_decider_video et
# fabriquer_noeud_generer_reponse invoquent reellement un LLM.
# fabriquer_noeud_rechercher_videos, plus bas, est 100% deterministe --
# il ne fait qu'executer RechercherVideosService avec la requete deja
# decidee par le LLM. Il est co-localise ici (et pas dans
# noeuds_agent.py) car il n'a de sens que dans ce graphe : le graphe de
# base (graphe_agent.py) ne cherche jamais de video.

# Bibliotheque standard
from   typing import Callable    # Typage des fabriques de noeuds

# Bibliotheques tierces
from   langchain_anthropic import ChatAnthropic    # Modele de decision
from   pydantic import BaseModel, Field             # Sortie structuree

# Modules internes
from   app.application.agent.etat_agent import EtatAgent    # Etat partage
from   app.application.rechercher_videos_service import (  # Cas
    RechercherVideosService,                                # d'usage
)
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="noeuds_agent_llm")


# ##############################################################################
# Fonction utilitaire : normalise reponse.content selon le fournisseur LLM
# ##############################################################################
def _extraire_texte(contenu) -> str:
    """Certains fournisseurs (Anthropic) renvoient reponse.content comme
    une simple chaine. D'autres (Google Gemini, via langchain_google_genai)
    renvoient une LISTE de blocs, ex. [{'type': 'text', 'text': '...'}].
    Cette fonction normalise les deux formats vers une chaine simple,
    quel que soit LLM_PROVIDER."""

    if isinstance(contenu, str):
        return contenu

    if isinstance(contenu, list):
        morceaux = []
        for bloc in contenu:
            if isinstance(bloc, str):
                morceaux.append(bloc)
            elif isinstance(bloc, dict) and "text" in bloc:
                morceaux.append(bloc["text"])
        return "".join(morceaux)

    return str(contenu)    # Repli de securite, ne devrait pas arriver


# ##############################################################################
# Schema de sortie structuree du LLM (pas de texte libre a parser)
# ##############################################################################
class DecisionVideo(BaseModel):
    """Decision du LLM : faut-il chercher une video, et avec quels termes."""

    rechercher_video: bool = Field(
        description=(
            "Vrai si une video explicative apporterait une valeur "
            "pedagogique reelle pour cette position (ex. ouverture connue "
            "et nommee). Faux si le contexte est deja suffisant, ou si "
            "aucune ouverture identifiable n'a ete trouvee."
        ),
    )
    requete_video: str = Field(
        default="",
        description=(
            "Si rechercher_video est vrai : le nom REEL de l'ouverture a "
            "utiliser comme terme de recherche (ex. 'Sicilian Najdorf', "
            "'Ruy Lopez'), pas le FEN. Chaine vide si rechercher_video est "
            "faux."
        ),
    )


# ------------------------------------------------------------------------
# Construction du prompt a partir de l'etat courant
# ------------------------------------------------------------------------
def _construire_resume_etat(etat: EtatAgent) -> str:
    coups = etat.get("coups_theoriques") or []
    extraits = etat.get("contexte_ouverture") or []

    lignes = [f"Position (FEN) : {etat['fen']}"]

    if coups:
        noms_coups = ", ".join(c.san for c in coups[:5])
        lignes.append(f"Coups theoriques connus : {noms_coups}")
    else:
        lignes.append("Aucun coup theorique connu pour cette position.")

    if extraits:
        lignes.append("Contexte pedagogique trouve :")
        for e in extraits[:3]:
            lignes.append(f"  - Ouverture : {e.ouverture} (score {e.score:.2f})")
    else:
        lignes.append("Aucun contexte pedagogique trouve (RAG vide).")

    return "\n".join(lignes)


# ##############################################################################
# Noeud : decision LLM sur la pertinence d'une recherche video
# ##############################################################################
def fabriquer_noeud_decider_video(
    modele: ChatAnthropic,
) -> Callable[[EtatAgent], dict]:
    """Construit le noeud de decision (LLM) sur la recherche de video.

    Se degrade avec une regle simple si l'appel LLM echoue (cle absente,
    quota, reseau) : ne bloque jamais le reste du graphe pour un point de
    decision secondaire, meme logique de repli que RechercherVideosService
    pour les erreurs YouTube.
    """

    def noeud_decider_video(etat: EtatAgent) -> dict:
        log.START_ACTION(
            "noeud_decider_video", "executer",
            "Decision LLM : rechercher une video explicative ?",
        )

        resume = _construire_resume_etat(etat)
        log.PARAMETER_VALUE("resume_etat", resume.replace("\n", " | "))

        try:
            modele_structure = modele.with_structured_output(DecisionVideo)
            decision: DecisionVideo = modele_structure.invoke(
                "Voici l'etat actuel de l'analyse d'une position d'echecs "
                "pour un jeune joueur en apprentissage des ouvertures :\n\n"
                f"{resume}\n\n"
                "Decide si une video explicative de l'ouverture aiderait "
                "reellement ce joueur, et si oui, quel nom d'ouverture "
                "utiliser comme requete de recherche.\n\n"
                "Criteres a appliquer strictement :\n"
                "- Recommande une video UNIQUEMENT si le contexte pedagogique "
                "converge clairement vers UNE SEULE famille d'ouverture "
                "(le meilleur score est nettement superieur aux autres, ou "
                "plusieurs extraits pointent vers la meme ouverture).\n"
                "- Ne recommande PAS de video si les extraits trouves pointent "
                "vers des ouvertures differentes et sans lien entre elles : "
                "cela signifie que la position n'est pas encore assez typee "
                "pour cibler une video pertinente.\n"
                "- Un coup theorique connu renforce la confiance dans le nom "
                "d'ouverture a utiliser comme requete.\n"
                "- En cas de doute, prefere ne pas recommander de video plutot "
                "que de risquer une requete hors sujet."
            )
            log.PARAMETER_VALUE("decision", decision.replace("\n", " | "))
            
        except Exception as erreur:
            # ------------------------------------------------------------
            # Repli : pas de LLM disponible -> heuristique simple plutot
            # que de casser le graphe pour un point de decision secondaire.
            # ------------------------------------------------------------
            log.LEVEL_6_NOTICE(
                "noeud_decider_video",
                f"Echec de l'appel LLM ({type(erreur).__name__}), repli "
                f"sur une heuristique simple : {erreur}",
            )
            extraits = etat.get("contexte_ouverture") or []
            decision = DecisionVideo(
                rechercher_video=bool(extraits),
                requete_video=extraits[0].ouverture if extraits else "",
            )

        log.FINISH_ACTION(
            "noeud_decider_video", "executer",
            f"rechercher_video={decision.rechercher_video}, "
            f"requete_video='{decision.requete_video}'",
        )
        return {
            "rechercher_video": decision.rechercher_video,
            "requete_video"   : decision.requete_video,
        }

    return noeud_decider_video


# ##############################################################################
# Arete conditionnelle : suivre ou non la decision du LLM
# ##############################################################################
def decider_apres_video(etat: EtatAgent) -> str:
    if etat.get("rechercher_video"):
        return "rechercher"
    return "fin"


# ##############################################################################
# Noeud : synthese en langage naturel (dernier maillon du graphe)
# ##############################################################################
def _construire_resume_pour_synthese(etat: EtatAgent) -> str:
    """Reutilise le meme resume que la decision video, en y ajoutant
    l'evaluation Stockfish et les videos, s'il y en a."""

    lignes = [_construire_resume_etat(etat)]

    evaluation = etat.get("evaluation")
    if evaluation:
        lignes.append(
            f"Evaluation moteur : {evaluation.type}={evaluation.valeur} "
            f"(coup recommande : {evaluation.coup_recommande}, "
            f"profondeur {evaluation.profondeur})"
        )

    videos = etat.get("videos") or []
    if videos:
        lignes.append(f"Video disponible : {videos[0].titre} ({videos[0].chaine})")

    return "\n".join(lignes)


def fabriquer_noeud_generer_reponse(
    modele: ChatAnthropic,
) -> Callable[[EtatAgent], dict]:
    """Construit le noeud de synthese pedagogique en langage naturel.

    Dernier noeud du graphe : prend tout ce que les noeuds precedents ont
    accumule (theorie, evaluation, contexte RAG, video eventuelle) et le
    transforme en une explication courte pour un jeune joueur. Se degrade
    en repli textuel simple si le LLM echoue -- ne bloque jamais la
    reponse HTTP pour un probleme de generation de prose.
    """

    def noeud_generer_reponse(etat: EtatAgent) -> dict:
        log.START_ACTION(
            "noeud_generer_reponse", "executer",
            "Synthese pedagogique en langage naturel",
        )

        resume = _construire_resume_pour_synthese(etat)

        try:
            reponse = modele.invoke(
                "Tu es un professeur d'echecs pedagogue qui s'adresse a "
                "un jeune joueur en apprentissage des ouvertures. Voici "
                "ce que l'analyse automatique a trouve pour la position "
                f"actuelle :\n\n{resume}\n\n"
                "Explique-lui en 2 a 4 phrases simples et encourageantes "
                "ce qu'il doit retenir de cette position, sans jargon "
                "technique inutile."
            )
            explication = _extraire_texte(reponse.content)

        except Exception as erreur:
            log.LEVEL_6_NOTICE(
                "noeud_generer_reponse",
                f"Echec de l'appel LLM ({type(erreur).__name__}), repli "
                f"sur une explication generique : {erreur}",
            )
            coups = etat.get("coups_theoriques") or []
            if coups:
                explication = (
                    f"Cette position est theorique : {coups[0].san} est un "
                    "coup solide et frequemment joue a ce niveau."
                )
            else:
                explication = (
                    "Cette position sort des sentiers battus -- c'est "
                    "l'occasion de reflechir par toi-meme avant de "
                    "regarder l'evaluation du moteur."
                )

        log.FINISH_ACTION(
            "noeud_generer_reponse", "executer",
            f"{len(explication)} caractere(s) generes",
        )
        return {"explication": explication}

    return noeud_generer_reponse


# ##############################################################################
# Noeud : execution de la recherche video (deterministe -- la decision
# elle-meme vient du LLM, juste au-dessus dans ce meme fichier)
# ##############################################################################
def fabriquer_noeud_rechercher_videos(
    service: RechercherVideosService,
) -> Callable[[EtatAgent], dict]:
    """Construit le noeud d'execution de la recherche video.

    N'est jamais atteint si le LLM a decide rechercher_video=False --
    voir decider_apres_video, plus haut, pour l'arete conditionnelle.
    """

    def noeud_rechercher_videos(etat: EtatAgent) -> dict:
        requete = etat.get("requete_video") or etat["fen"]

        log.START_ACTION(
            "noeud_rechercher_videos", "executer",
            "Execution de la recherche video decidee par le LLM",
        )
        log.PARAMETER_VALUE("requete_video", requete)

        videos = service.executer(requete)

        log.FINISH_ACTION(
            "noeud_rechercher_videos", "executer",
            f"{len(videos)} video(s) trouvee(s)",
        )
        return {"videos": videos}

    return noeud_rechercher_videos
