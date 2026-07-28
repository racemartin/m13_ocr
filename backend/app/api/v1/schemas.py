# ############################################################################
# Schemas Pydantic de la couche presentation
# ############################################################################
# Ces schemas ne sont utilises que pour serialiser les reponses HTTP. Ils
# sont volontairement separes des modeles de domaine (dataclasses) afin de
# ne jamais coupler le contrat HTTP a la representation interne du metier.

# Bibliotheques tierces
from   pydantic import BaseModel    # Validation et serialisation

# Modules internes
from   app.domaine.modeles import CoupTheorique, Evaluation    # Modeles


class CoupTheoriqueSchema(BaseModel):
    uci             : str
    san             : str
    nombre_parties  : int

    @staticmethod
    def depuis_domaine(coup: CoupTheorique) -> "CoupTheoriqueSchema":
        return CoupTheoriqueSchema(
            uci            = coup.uci,
            san            = coup.san,
            nombre_parties = coup.nombre_parties,
        )


class EvaluationSchema(BaseModel):
    type   : str
    valeur : int

    @staticmethod
    def depuis_domaine(evaluation: Evaluation) -> "EvaluationSchema":
        return EvaluationSchema(type=evaluation.type, valeur=evaluation.valeur)
