FROM python:3.10-slim

# ---------------------------------------------
#   ENV
# ---------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    ALEMBIC_CONFIG=/usr/src/alembic/alembic.ini \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME="/opt/poetry"

# ---------------------------------------------
#   System dependencies
# ---------------------------------------------
RUN apt update && apt install -y --no-install-recommends \
    gcc \
    libpq-dev \
    netcat-openbsd \
    postgresql-client \
    dos2unix \
    && apt clean && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------
#   Install Poetry
# ---------------------------------------------
RUN pip install --no-cache-dir poetry

# ---------------------------------------------
#   Copy dependencies files
# ---------------------------------------------
COPY ./poetry.lock ./pyproject.toml /usr/src/poetry/
COPY ./alembic.ini /usr/src/alembic/alembic.ini

WORKDIR /usr/src/poetry

# ---------------------------------------------
#   Install python dependencies
# ---------------------------------------------
RUN poetry install --no-root --only main

# ---------------------------------------------
#   Copy app source code
# ---------------------------------------------
WORKDIR /usr/src/fastapi
COPY ./src .

# ---------------------------------------------
#   Copy shell scripts
# ---------------------------------------------
COPY ./commands /commands
RUN dos2unix /commands/*.sh && chmod +x /commands/*.sh

EXPOSE 8000
