#!/usr/bin/env python
# ############################################################################
# Smoke-test de l'appel Gemini -- AUCUNE dependance au graphe/Docker/FastAPI
# ############################################################################
# Reproduit EXACTEMENT ce que fait obtenir_modele_decision() dans
# dependances.py, mais isole -- pour iterer vite sans reconstruire Docker
# a chaque essai.
#
# Utilisation :
#   cd backend
#   uv run python scripts/test_gemini_smoke.py

import os
import sys

from dotenv import load_dotenv

load_dotenv()

nom_modele = os.environ.get("GOOGLE_MODEL", "")
cle_api = os.environ.get("GOOGLE_API_KEY", "")

print("=" * 70)
print("1. INSPECTION BRUTE DE LA VARIABLE (revele les caracteres invisibles)")
print("=" * 70)
print(f"GOOGLE_MODEL (repr)     : {nom_modele!r}")
print(f"GOOGLE_MODEL (longueur) : {len(nom_modele)} caracteres")
print(f"GOOGLE_MODEL (codes)    : {[hex(ord(c)) for c in nom_modele]}")
print()

if not cle_api:
    print("Erreur : GOOGLE_API_KEY absente.")
    sys.exit(1)

print("=" * 70)
print("2. APPEL REEL A GEMINI (identique a obtenir_modele_decision())")
print("=" * 70)

from langchain_google_genai import ChatGoogleGenerativeAI

modele = ChatGoogleGenerativeAI(model=nom_modele)

try:
    reponse = modele.invoke("Reponds uniquement par le mot : OK")
    print("Reponse recue avec succes :")
    print(f"  {reponse.content!r}")
    sys.exit(0)
except Exception as erreur:
    print(f"ECHEC : {type(erreur).__name__}")
    print(f"  {erreur}")
    sys.exit(1)
