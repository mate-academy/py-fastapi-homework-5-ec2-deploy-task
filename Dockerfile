# Build stage
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1

RUN pip install poetry==2.5.1
RUN python -m venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /usr/src/poetry

COPY ./poetry.lock ./pyproject.toml ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main --no-cache \
    && /opt/venv/bin/python -m pip uninstall -y pip

# Production stage
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV ALEMBIC_CONFIG=/usr/src/alembic/alembic.ini

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./alembic.ini /usr/src/alembic/alembic.ini

WORKDIR /usr/src/fastapi

COPY ./src .
COPY ./commands /commands

RUN chmod +x /commands/*.sh