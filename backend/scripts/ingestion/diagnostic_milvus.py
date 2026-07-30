# ############################################################################
# Script de diagnostic : inspecte le contenu reel de la collection Milvus
# ############################################################################
# A lancer depuis la machine hote (pas depuis un conteneur) : utilise donc
# "localhost:19530" (le port publie), pas "milvus-standalone:19530" (nom
# DNS uniquement resolu depuis l'interieur du reseau Docker).

import sys
from   pathlib import Path

racine_backend = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(racine_backend))

from pymilvus import MilvusClient

NOM_COLLECTION = "ouvertures_echecs"

client = MilvusClient(uri="http://localhost:19530")

print("--- Collections existantes ---")
collections = client.list_collections()
print(collections)

if NOM_COLLECTION not in collections:
    print(f"\nLa collection '{NOM_COLLECTION}' n'existe pas encore.")
    print("As-tu deja lance indexer_corpus.py ?")
    sys.exit(0)

print(f"\n--- Details de la collection '{NOM_COLLECTION}' ---")
description = client.describe_collection(NOM_COLLECTION)
print("Champs :", [c["name"] for c in description["fields"]])

print("\n--- Nombre d'entites ---")
stats = client.get_collection_stats(NOM_COLLECTION)
print(stats)

print("\n--- 5 premiers documents (echantillon) ---")
resultats = client.query(
    collection_name=NOM_COLLECTION,
    filter="",
    output_fields=["texte", "ouverture", "source_url"],
    limit=5,
)
for i, doc in enumerate(resultats, start=1):
    print(f"\n[{i}] ouverture : {doc.get('ouverture')}")
    print(f"    source    : {doc.get('source_url')}")
    print(f"    texte     : {doc.get('texte', '')[:100]}...")
