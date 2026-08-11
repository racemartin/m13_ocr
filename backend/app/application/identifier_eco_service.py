# ############################################################################
# Cas d'utilisation : identifier le code ECO d'une position
# ############################################################################
# Delegue au port d'identification ECO. Aucune connaissance de la source
# des donnees (index precalcule, dataset Lichess) ici -- uniquement
# l'orchestration du cas d'utilisation.

# Modules internes
from   app.domaine.modeles import InfoEco
from   app.domaine.ports.port_identification_eco import PortIdentificationEco
from   app.tools.rafael.log_tool import LogTool    # Journalisation coloree

log = LogTool(origin="identifier_eco_service")


class IdentifierEcoService:
    def __init__(self, identification_eco: PortIdentificationEco) -> None:
        self.identification_eco = identification_eco

    # ------------------------------------------------------------------
    # Delegue directement au port -- pas de logique metier additionnelle
    # ------------------------------------------------------------------
    def executer(self, fen: str) -> InfoEco | None:
        log.START_ACTION(
            "IdentifierEcoService", "executer", "Identification ECO",
        )
        log.PARAMETER_VALUE("fen", fen)

        resultat = self.identification_eco.identifier(fen)

        log.FINISH_ACTION(
            "IdentifierEcoService", "executer",
            f"{resultat.code if resultat else 'aucun code'} trouve",
        )
        return resultat
