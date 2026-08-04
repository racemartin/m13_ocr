#!/usr/bin/env python
# ############################################################################
# Script de test manuel des endpoints (healthcheck, moves, evaluate, videos)
# ############################################################################
# A lancer contre un backend deja demarre (Docker ou "uv run uvicorn ...").
# N'utilise aucune bibliotheque de test : verification manuelle rapide,
# complementaire des tests automatises du dossier tests/.
#
# Chaque test est annonce et chronometre via LogTool (meme outil que le
# reste du projet), avec le corps de chaque reponse affiche de facon
# structuree (LOG_DICT), pas juste un status code brut.
#
# Utilisation :
#   uv run python scripts/test_endpoints.py
#   uv run python scripts/test_endpoints.py --base-url http://localhost:8081

# Bibliotheque standard
import argparse    # Lecture des arguments de la ligne de commande
import sys         # Code de sortie du script

# Bibliotheques tierces
import httpx    # Client HTTP (deja utilise par le backend)

# Modules internes
from app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="test_endpoints")

# Position de depart standard, utilisee pour les endpoints /moves et
# /evaluate. Elle est theorique par definition : Lichess doit repondre.
FEN_POSITION_DEPART = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
)

# Position volontairement invalide, pour verifier le code 422
FEN_INVALIDE = "ceci-nest-pas-un-fen"

# Ouverture utilisee pour l'endpoint /videos
OUVERTURE_TEST = "Sicilienne"

DELAI_TIMEOUT_SECONDES = 15.0
LIMITE_ELEMENTS_AFFICHES = 3    # Evite d'inonder la console sur une longue liste


# ------------------------------------------------------------------------
# Affichage structure du corps d'une reponse, quelle que soit sa forme
# ------------------------------------------------------------------------
def _corps_json_ou_texte(reponse: httpx.Response):
    try:
        return reponse.json()
    except ValueError:
        return reponse.text


def _afficher_reponse(corps) -> None:
    """Affiche le corps d'une reponse de facon lisible via LOG_DICT.

    Gere les 3 formes possibles renvoyees par l'API : un dict (ex.
    /evaluate), une liste de dicts (ex. /moves, /videos), ou du texte brut
    (erreurs, reponses non-JSON).
    """
    if isinstance(corps, list):
        log.PARAMETER_VALUE("nombre_elements", len(corps))
        for i, element in enumerate(corps[:LIMITE_ELEMENTS_AFFICHES]):
            if isinstance(element, dict):
                log.LOG_DICT(element, f"element[{i}]")
            else:
                log.PARAMETER_VALUE(f"element[{i}]", element)
        restants = len(corps) - LIMITE_ELEMENTS_AFFICHES
        if restants > 0:
            log.PARAMETER_VALUE("...", f"{restants} element(s) non affiche(s)")

    elif isinstance(corps, dict):
        log.LOG_DICT(corps, "corps")

    else:
        log.PARAMETER_VALUE("corps", corps)


# ------------------------------------------------------------------------
# Verifications individuelles -- chacune annoncee/chronometree par LogTool
# ------------------------------------------------------------------------
def verifier_healthcheck(client: httpx.Client) -> bool:
    log.START_ACTION(
        "test_endpoints", "verifier_healthcheck", "GET /api/v1/healthcheck",
    )
    try:
        reponse = client.get("/api/v1/healthcheck")
    except httpx.RequestError as erreur:
        log.LEVEL_4_ERROR("verifier_healthcheck", f"connexion impossible : {erreur}")
        log.FINISH_ACTION("test_endpoints", "verifier_healthcheck", "ECHEC")
        return False

    log.PARAMETER_VALUE("status_code", reponse.status_code)
    _afficher_reponse(_corps_json_ou_texte(reponse))

    ok = reponse.status_code == 200
    (log.LEVEL_7_INFO if ok else log.LEVEL_4_ERROR)(
        "verifier_healthcheck", "OK" if ok else "status inattendu",
    )
    log.FINISH_ACTION(
        "test_endpoints", "verifier_healthcheck", "OK" if ok else "ECHEC",
    )
    return ok


def verifier_moves(client: httpx.Client) -> bool:
    log.START_ACTION(
        "test_endpoints", "verifier_moves",
        "GET /api/v1/moves/{fen} (position theorique)",
    )
    try:
        reponse = client.get(f"/api/v1/moves/{FEN_POSITION_DEPART}")
    except httpx.RequestError as erreur:
        log.LEVEL_4_ERROR("verifier_moves", str(erreur))
        log.FINISH_ACTION("test_endpoints", "verifier_moves", "ECHEC")
        return False

    log.PARAMETER_VALUE("status_code", reponse.status_code)
    _afficher_reponse(_corps_json_ou_texte(reponse))

    ok = reponse.status_code == 200
    (log.LEVEL_7_INFO if ok else log.LEVEL_4_ERROR)(
        "verifier_moves", "OK" if ok else "status inattendu",
    )
    log.FINISH_ACTION("test_endpoints", "verifier_moves", "OK" if ok else "ECHEC")
    return ok


def verifier_moves_fen_invalide(client: httpx.Client) -> bool:
    log.START_ACTION(
        "test_endpoints", "verifier_moves_fen_invalide",
        "GET /api/v1/moves/{fen} (FEN invalide -> 422 attendu)",
    )
    try:
        reponse = client.get(f"/api/v1/moves/{FEN_INVALIDE}")
    except httpx.RequestError as erreur:
        log.LEVEL_4_ERROR("verifier_moves_fen_invalide", str(erreur))
        log.FINISH_ACTION("test_endpoints", "verifier_moves_fen_invalide", "ECHEC")
        return False

    log.PARAMETER_VALUE("status_code", reponse.status_code)
    _afficher_reponse(_corps_json_ou_texte(reponse))

    ok = reponse.status_code == 422
    (log.LEVEL_7_INFO if ok else log.LEVEL_4_ERROR)(
        "verifier_moves_fen_invalide", "OK" if ok else "status inattendu",
    )
    log.FINISH_ACTION(
        "test_endpoints", "verifier_moves_fen_invalide", "OK" if ok else "ECHEC",
    )
    return ok


def verifier_evaluate(client: httpx.Client) -> bool:
    log.START_ACTION(
        "test_endpoints", "verifier_evaluate",
        "GET /api/v1/evaluate/{fen} (position de depart)",
    )
    try:
        reponse = client.get(f"/api/v1/evaluate/{FEN_POSITION_DEPART}")
    except httpx.RequestError as erreur:
        log.LEVEL_4_ERROR("verifier_evaluate", str(erreur))
        log.FINISH_ACTION("test_endpoints", "verifier_evaluate", "ECHEC")
        return False

    log.PARAMETER_VALUE("status_code", reponse.status_code)
    _afficher_reponse(_corps_json_ou_texte(reponse))

    ok = reponse.status_code == 200
    (log.LEVEL_7_INFO if ok else log.LEVEL_4_ERROR)(
        "verifier_evaluate", "OK" if ok else "status inattendu",
    )
    log.FINISH_ACTION(
        "test_endpoints", "verifier_evaluate", "OK" if ok else "ECHEC",
    )
    return ok


def verifier_videos(client: httpx.Client) -> bool:
    log.START_ACTION(
        "test_endpoints", "verifier_videos",
        f"GET /api/v1/videos/{{ouverture}} (ouverture={OUVERTURE_TEST})",
    )
    try:
        reponse = client.get(f"/api/v1/videos/{OUVERTURE_TEST}")
    except httpx.RequestError as erreur:
        log.LEVEL_4_ERROR("verifier_videos", str(erreur))
        log.FINISH_ACTION("test_endpoints", "verifier_videos", "ECHEC")
        return False

    log.PARAMETER_VALUE("status_code", reponse.status_code)
    _afficher_reponse(_corps_json_ou_texte(reponse))

    ok = reponse.status_code == 200
    (log.LEVEL_7_INFO if ok else log.LEVEL_4_ERROR)(
        "verifier_videos", "OK" if ok else "status inattendu",
    )
    log.FINISH_ACTION(
        "test_endpoints", "verifier_videos", "OK" if ok else "ECHEC",
    )
    return ok


# ------------------------------------------------------------------------
# Registre des tests disponibles -- cle utilisee par --test
# ------------------------------------------------------------------------
TESTS_DISPONIBLES = {
    "healthcheck"      : verifier_healthcheck,
    "moves"            : verifier_moves,
    "moves-invalide"   : verifier_moves_fen_invalide,
    "evaluate"         : verifier_evaluate,
    "videos"           : verifier_videos,
}


# ------------------------------------------------------------------------
# Point d'entree
# ------------------------------------------------------------------------
def main() -> int:
    analyseur = argparse.ArgumentParser(
        description="Verifie manuellement les endpoints du backend FFE.",
    )
    analyseur.add_argument(
        "--base-url", default="http://localhost:8000",
        help="URL de base du backend (defaut: http://localhost:8000)",
    )
    analyseur.add_argument(
        "--test", choices=sorted(TESTS_DISPONIBLES), default=None,
        help="Lance uniquement ce test au lieu de tous "
             f"({', '.join(sorted(TESTS_DISPONIBLES))}).",
    )
    arguments = analyseur.parse_args()

    log.PARAMETER_VALUE("Backend cible", arguments.base_url)
    if arguments.test:
        log.PARAMETER_VALUE("Test unique", arguments.test)

    tests_a_lancer = (
        {arguments.test: TESTS_DISPONIBLES[arguments.test]}
        if arguments.test
        else TESTS_DISPONIBLES
    )

    with httpx.Client(
        base_url=arguments.base_url, timeout=DELAI_TIMEOUT_SECONDES,
    ) as client:
        resultats = [fonction(client) for fonction in tests_a_lancer.values()]

    if all(resultats):
        log.LEVEL_7_INFO(
            "test_endpoints", f"Tous les tests sont passes ({len(resultats)}/{len(resultats)})",
        )
        return 0

    nb_echecs = resultats.count(False)
    log.LEVEL_4_ERROR(
        "test_endpoints",
        f"{nb_echecs}/{len(resultats)} test(s) en echec -- voir le detail ci-dessus",
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())