"""Configuration centralisee de l'application, lue depuis l'env."""

# ----------------------------------------------------------------
# Bibliotheque tierce pour la gestion typee des variables d'env
# ----------------------------------------------------------------
from pydantic_settings import BaseSettings  # chargement config .env


class Parametres(BaseSettings):
    """Regroupe toutes les variables de configuration de l'API.

    Chaque attribut correspond a une variable d'environnement du
    meme nom (en majuscules). Les valeurs par defaut ci-dessous ne
    sont utilisees que si la variable n'est pas definie dans .env.
    """

    nom_application : str = "FFE Chess Agent - Backend"
    version_api     : str = "0.1.0"
    backend_port    : int = 8000

    class Config:
        """Indique a Pydantic ou lire le fichier d'environnement."""

        env_file = ".env"


# Instance unique reutilisee dans toute l'application (singleton)
parametres = Parametres()
