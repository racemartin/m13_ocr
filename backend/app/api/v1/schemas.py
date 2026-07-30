# ############################################################################
# Schemas Pydantic de la couche presentation
# ############################################################################
# Ces schemas ne sont utilises que pour serialiser les reponses HTTP. Ils
# sont volontairement separes des modeles de domaine (dataclasses) afin de
# ne jamais coupler le contrat HTTP a la representation interne du metier.

# Bibliotheque standard
from   typing import Literal    # Discriminant "theorie" | "evaluation"

# Bibliotheques tierces
from   pydantic import BaseModel    # Validation et serialisation

# Modules internes
from   app.domaine.modeles import (    # Modeles
    CoupTheorique, Evaluation, ExtraitConnaissance, ResultatExploration,
)


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
    type  : str
    value : int
    score : str    # Format lisible, ex. "+0.35" ou "#3"


def _formater_score(evaluation: Evaluation) -> str:
    """Convertit l'evaluation brute en score lisible (ex. '+0.35', '#3')."""
    if evaluation.type == "mate":
        signe = "+" if evaluation.valeur >= 0 else "-"
        return f"{signe}#{abs(evaluation.valeur)}"

    pions = evaluation.valeur / 100
    signe = "+" if pions >= 0 else ""
    return f"{signe}{pions:.2f}"


class EvaluationSchema(BaseModel):
    fen       : str
    evaluation: DetailEvaluationSchema
    best_move : str | None
    depth     : int

    @staticmethod
    def depuis_domaine(fen: str, evaluation: Evaluation) -> "EvaluationSchema":
        return EvaluationSchema(
            fen        = fen,
            evaluation = DetailEvaluationSchema(
                type  = evaluation.type,
                value = evaluation.valeur,
                score = _formater_score(evaluation),
            ),
            best_move = evaluation.coup_recommande,
            depth     = evaluation.profondeur,
        )


# ------------------------------------------------------------------------
# Schemas de /explore/{fen} : reponse discriminee par le champ "type"
# ------------------------------------------------------------------------
class ExplorationTheorieSchema(BaseModel):
    fen   : str
    type  : Literal["theorie"]
    coups : list[CoupTheoriqueSchema]


class ExplorationEvaluationSchema(BaseModel):
    fen        : str
    type       : Literal["evaluation"]
    evaluation : DetailEvaluationSchema
    best_move  : str | None
    depth      : int


def resultat_exploration_vers_schema(
    fen: str, resultat: ResultatExploration,
) -> ExplorationTheorieSchema | ExplorationEvaluationSchema:
    """Convertit le resultat de domaine vers le schema HTTP adapte."""
    if resultat.type == "theorie":
        return ExplorationTheorieSchema(
            fen   = fen,
            type  = "theorie",
            coups = [
                CoupTheoriqueSchema.depuis_domaine(coup)
                for coup in resultat.coups
            ],
        )

    evaluation = resultat.evaluation
    return ExplorationEvaluationSchema(
        fen        = fen,
        type       = "evaluation",
        evaluation = DetailEvaluationSchema(
            type  = evaluation.type,
            value = evaluation.valeur,
            score = _formater_score(evaluation),
        ),
        best_move = evaluation.coup_recommande,
        depth     = evaluation.profondeur,
    )


# ------------------------------------------------------------------------
# Schema de /vector-search : contexte retrouve par recherche vectorielle
# ------------------------------------------------------------------------
class ExtraitConnaissanceSchema(BaseModel):
    texte      : str
    ouverture  : str
    source_url : str
    score      : float

    @staticmethod
    def depuis_domaine(
        extrait: ExtraitConnaissance,
    ) -> "ExtraitConnaissanceSchema":
        return ExtraitConnaissanceSchema(
            texte      = extrait.texte,
            ouverture  = extrait.ouverture,
            source_url = extrait.source_url,
            score      = extrait.score,
        )
