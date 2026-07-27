# ---------------------------------------------------------------
# Image de base : version figee pour garantir la reproductibilite
# ---------------------------------------------------------------
FROM python:3.12-slim

# Installation de uv (gestionnaire de paquets Python rapide)
COPY --from=ghcr.io/astral-sh/uv:0.5.0 /uv /uvx /bin/

WORKDIR /code

# Copie des seuls fichiers de dependances d'abord (cache Docker)
COPY pyproject.toml uv.lock README.md ./

# Installation reproductible depuis le lockfile (sans les groupes dev/test)
RUN uv sync --frozen --no-dev --no-group test

# Copie du code applicatif
COPY app ./app

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:application", \
     "--host", "0.0.0.0", "--port", "8000"]
