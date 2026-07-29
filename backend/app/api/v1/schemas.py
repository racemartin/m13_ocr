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


class DetailEvaluationSchema(BaseModel):
    type   : str
    valeur : int
    score  : str    # Format lisible, ex. "+0.35" ou "#3"


def _formater_score(evaluation: Evaluation) -> str:
    """Convertit l'evaluation brute en score lisible (ex. '+0.35', '#3')."""
    if evaluation.type == "mate":
        signe = "+" if evaluation.valeur >= 0 else "-"
        return f"{signe}#{abs(evaluation.valeur)}"

    pions = evaluation.valeur / 100
    signe = "+" if pions >= 0 else ""
    return f"{signe}{pions:.2f}"


class EvaluationSchema(BaseModel):
    fen             : str
    evaluation      : DetailEvaluationSchema
    coup_recommande : str | None
    profondeur      : int

    @staticmethod
    def depuis_domaine(fen: str, evaluation: Evaluation) -> "EvaluationSchema":
        return EvaluationSchema(
            fen        = fen,
            evaluation = DetailEvaluationSchema(
                type   = evaluation.type,
                valeur = evaluation.valeur,
                score  = _formater_score(evaluation),
            ),
            coup_recommande = evaluation.coup_recommande,
            profondeur      = evaluation.profondeur,
        )
