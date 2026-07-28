#!/usr/bin/env python
# ############################################################################
# Script de test manuel des endpoints (healthcheck, moves, evaluate)
# ############################################################################
# A lancer contre un backend deja demarre (Docker ou "uv run uvicorn ...").
# N'utilise aucune bibliotheque de test : verification manuelle rapide,
# complementaire des tests automatises du dossier tests/.
#
# Utilisation :
#   uv run python scripts/test_endpoints.py
#   uv run python scripts/test_endpoints.py --base-url http://localhost:8081

# Bibliotheque standard
import argparse    # Lecture des arguments de la ligne de commande
import sys         # Code de sortie du script

# Bibliotheques tierces
import httpx    # Client HTTP (deja utilise par le backend)

# Position de depart standard, utilisee pour les endpoints /moves et
# /evaluate. Elle est theorique par definition : Lichess doit repondre.
FEN_POSITION_DEPART = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
)

# Position volontairement invalide, pour verifier le code 422
FEN_INVALIDE = "ceci-nest-pas-un-fen"

DELAI_TIMEOUT_SECONDES = 15.0


# ------------------------------------------------------------------------
# Affichage coloree du resultat d'un test
# ------------------------------------------------------------------------
def afficher_resultat(nom: str, ok: bool, detail: str) -> None:
    etiquette = " OK " if ok else "ECHEC"
    print(f"[{etiquette}] {nom:<38} {detail}")


# ------------------------------------------------------------------------
# Verifications individuelles
# ------------------------------------------------------------------------
def verifier_healthcheck(client: httpx.Client) -> bool:
    try:
        reponse = client.get("/api/v1/healthcheck")
    except httpx.RequestError as erreur:
        afficher_resultat("healthcheck", False, f"connexion impossible : {erreur}")
        return False

    ok = reponse.status_code == 200
    afficher_resultat("healthcheck", ok, f"{reponse.status_code} {reponse.text}")
    return ok


def verifier_moves(client: httpx.Client) -> bool:
    try:
        reponse = client.get(f"/api/v1/moves/{FEN_POSITION_DEPART}")
    except httpx.RequestError as erreur:
        afficher_resultat("moves (position theorique)", False, str(erreur))
        return False

    ok = reponse.status_code == 200
    nb_coups = len(reponse.json()) if ok else 0
    afficher_resultat(
        "moves (position theorique)", ok,
        f"{reponse.status_code} — {nb_coups} coup(s) theorique(s)",
    )
    return ok


def verifier_moves_fen_invalide(client: httpx.Client) -> bool:
    try:
        reponse = client.get(f"/api/v1/moves/{FEN_INVALIDE}")
    except httpx.RequestError as erreur:
        afficher_resultat("moves (FEN invalide -> 422)", False, str(erreur))
        return False

    ok = reponse.status_code == 422
    afficher_resultat(
        "moves (FEN invalide -> 422)", ok, f"{reponse.status_code}",
    )
    return ok


def verifier_evaluate(client: httpx.Client) -> bool:
    try:
        reponse = client.get(f"/api/v1/evaluate/{FEN_POSITION_DEPART}")
    except httpx.RequestError as erreur:
        afficher_resultat("evaluate (position de depart)", False, str(erreur))
        return False

    ok = reponse.status_code == 200
    afficher_resultat(
        "evaluate (position de depart)", ok,
        f"{reponse.status_code} {reponse.text}",
    )
    return ok


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
    arguments = analyseur.parse_args()

    print(f"Backend cible : {arguments.base_url}\n")

    with httpx.Client(
        base_url=arguments.base_url, timeout=DELAI_TIMEOUT_SECONDES,
    ) as client:
        resultats = [
            verifier_healthcheck(client),
            verifier_moves(client),
            verifier_moves_fen_invalide(client),
            verifier_evaluate(client),
        ]

    print()
    if all(resultats):
        print("Tous les tests manuels sont passes.")
        return 0

    print("Au moins un test manuel a echoue — voir le detail ci-dessus.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
