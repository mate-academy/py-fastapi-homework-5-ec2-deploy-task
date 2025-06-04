FROM python:3.13-alpine

# Setting environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off
ENV ALEMBIC_CONFIG=/usr/src/alembic/alembic.ini

# Install system dependencies using apk
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libpq \
    netcat-openbsd \
    dos2unix \
    bash \
    curl \
    build-base \
    && rm -rf /var/cache/apk/*

# Install Poetry
RUN python -m pip install --upgrade pip && \
    pip install poetry

# Copy dependency files
COPY ./poetry.lock /usr/src/poetry/poetry.lock
COPY ./pyproject.toml /usr/src/poetry/pyproject.toml
COPY ./alembic.ini /usr/src/alembic/alembic.ini

# Configure Poetry to avoid creating a virtual environment
RUN poetry config virtualenvs.create false

# Set working directory to install dependencies
WORKDIR /usr/src/poetry

# Install dependencies
RUN poetry install --no-root --only main

# Set working directory for application
WORKDIR /usr/src/fastapi

# Copy the source code
COPY ./src .

# Copy command scripts
COPY ./commands /commands

# Ensure Unix-style line endings and executable permissions for scripts
RUN dos2unix /commands/*.sh && chmod +x /commands/*.sh
