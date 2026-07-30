from pymilvus import MilvusClient
client = MilvusClient(uri="http://localhost:19530")
if client.has_collection("ouvertures_echecs"):
    client.drop_collection("ouvertures_echecs")
    print("Coleccion 'ouvertures_echecs' eliminada.")
else:
    print("La coleccion no existia.")