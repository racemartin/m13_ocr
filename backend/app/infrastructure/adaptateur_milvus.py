# ############################################################################
# Adaptateur d'infrastructure : base de connaissances vectorielle (Milvus)
# ############################################################################
# Seul module du systeme qui importe pymilvus et sentence-transformers.
# Implemente le port PortBaseConnaissances defini par le domaine.

# Bibliotheque standard
import re                     # Analyse du frontmatter YAML minimal
from   pathlib import Path    # Parcours des fichiers .md du corpus

# Bibliotheques tierces
from   pymilvus import MilvusClient              # Client Milvus (API moderne)
from   sentence_transformers import SentenceTransformer  # Embeddings

# Modules internes
from   app.domaine.modeles import ExtraitConnaissance        # Modele
from   app.domaine.ports.port_base_connaissances import (    # Port a
    PortBaseConnaissances,                                   # implementer
)
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="adaptateur_milvus")

NOM_COLLECTION = "ouvertures_echecs"


# ------------------------------------------------------------------------
# Analyse minimale du frontmatter YAML des documents corpus/*.md
# ------------------------------------------------------------------------
# NOTE : parseur volontairement simple (regex, pas de dependance YAML
# supplementaire) -- le frontmatter genere par build_corpus.py est
# toujours plat (cle: valeur), jamais imbrique.
def _analyser_frontmatter(contenu: str) -> tuple[dict, str]:
    correspondance = re.match(r"^---\n(.*?)\n---\n\n(.*)$", contenu, re.S)
    if not correspondance:
        return {}, contenu

    bloc_frontmatter, corps = correspondance.groups()
    frontmatter = {}
    for ligne in bloc_frontmatter.splitlines():
        if ":" in ligne:
            cle, _, valeur = ligne.partition(":")
            frontmatter[cle.strip()] = valeur.strip()

    return frontmatter, corps.strip()


class AdaptateurMilvus(PortBaseConnaissances):
    def __init__(
        self,
        hote               : str,
        port               : str,
        nom_modele_embeddings : str,
    ) -> None:
        self.client = MilvusClient(uri=f"http://{hote}:{port}")
        self.modele = SentenceTransformer(nom_modele_embeddings)
        self._assurer_collection()

    # ------------------------------------------------------------------
    # Cree la collection si necessaire (idempotent)
    # ------------------------------------------------------------------
    def _assurer_collection(self) -> None:
        if self.client.has_collection(NOM_COLLECTION):
            return

        log.LEVEL_7_INFO(
            "AdaptateurMilvus", f"Creation de la collection {NOM_COLLECTION}",
        )
        self.client.create_collection(
            collection_name = NOM_COLLECTION,
            dimension       = self.modele.get_embedding_dimension(),
            metric_type     = "COSINE",
            auto_id         = True,    # Milvus genere l'id, on ne le fournit pas
        )

    # ------------------------------------------------------------------
    # Indexation : lit data/corpus/*.md, calcule les embeddings, insere
    # ------------------------------------------------------------------
    def indexer_documents(self, dossier: str) -> int:
        log.START_ACTION(
            "AdaptateurMilvus", "indexer_documents",
            "Indexation du corpus dans Milvus",
        )
        log.PARAMETER_VALUE("dossier", dossier)

        chemins = sorted(Path(dossier).glob("*.md"))
        donnees = []

        for chemin in chemins:
            frontmatter, texte = _analyser_frontmatter(
                chemin.read_text(encoding="utf-8"),
            )
            if not texte:
                continue

            vecteur = self.modele.encode(
                texte, normalize_embeddings=True,
            ).tolist()
            donnees.append({
                "vector"     : vecteur,
                "texte"      : texte,
                "ouverture"  : frontmatter.get("nom", ""),
                "source_url" : frontmatter.get("url", ""),
            })

        if donnees:
            self.client.insert(collection_name=NOM_COLLECTION, data=donnees)

        log.PARAMETER_VALUE("documents_indexes", len(donnees))
        log.FINISH_ACTION(
            "AdaptateurMilvus", "indexer_documents",
            f"{len(donnees)} document(s) indexe(s)",
        )
        return len(donnees)

    # ------------------------------------------------------------------
    # Recherche vectorielle : requete -> extraits les plus proches
    # ------------------------------------------------------------------
    def rechercher_contexte(
        self, requete: str, top_k: int = 3,
    ) -> list[ExtraitConnaissance]:
        log.START_ACTION(
            "AdaptateurMilvus", "rechercher_contexte",
            "Recherche vectorielle de contexte",
        )
        log.PARAMETER_VALUE("requete", requete)
        log.PARAMETER_VALUE("top_k", top_k)

        vecteur = self.modele.encode(
            requete, normalize_embeddings=True,
        ).tolist()

        resultats = self.client.search(
            collection_name = NOM_COLLECTION,
            data             = [vecteur],
            limit            = top_k,
            output_fields    = ["texte", "ouverture", "source_url"],
        )

        extraits = [
            ExtraitConnaissance(
                texte      = correspondance["entity"]["texte"],
                ouverture  = correspondance["entity"]["ouverture"],
                source_url = correspondance["entity"]["source_url"],
                score      = correspondance["distance"],
            )
            for correspondance in resultats[0]
        ]

        log.PARAMETER_VALUE("nombre_extraits_trouves", len(extraits))
        log.FINISH_ACTION(
            "AdaptateurMilvus", "rechercher_contexte",
            f"{len(extraits)} extrait(s) trouve(s)",
        )
        return extraits
