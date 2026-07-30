# ############################################################################
# Script d'indexation : data/corpus/*.md -> Milvus
# ############################################################################
# A executer manuellement (ou via une tache planifiee) apres avoir genere
# le corpus (build_corpus.py). Volontairement separe du cycle de requetes
# de l'API : indexer n'est pas une operation a repeter a chaque appel.

# Bibliotheque standard
import sys
from   pathlib import Path

RACINE_BACKEND = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RACINE_BACKEND))

# Modules internes
from   app.core.dependances import obtenir_adaptateur_milvus
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="indexer_corpus")


def main() -> None:
    log.START_ACTION(
        "indexer_corpus", "main", "Indexation du corpus dans Milvus",
    )

    dossier_corpus = str(RACINE_BACKEND / "data" / "corpus")
    log.PARAMETER_VALUE("dossier_corpus", dossier_corpus)

    adaptateur = obtenir_adaptateur_milvus()
    total = adaptateur.indexer_documents(dossier_corpus)

    log.PARAMETER_VALUE("documents_indexes", total)
    log.FINISH_ACTION(
        "indexer_corpus", "main", f"{total} document(s) indexe(s)",
    )


if __name__ == "__main__":
    main()
