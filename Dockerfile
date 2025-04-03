# Використовуємо легший образ
FROM python:3.10-slim AS base

# Встановлюємо необхідні пакети
RUN apt update && apt install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Налаштовуємо Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    ALEMBIC_CONFIG=/usr/src/alembic/alembic.ini

# Встановлюємо Poetry
RUN python -m pip install --upgrade pip && \
    pip install poetry

# Створюємо директорію для коду
WORKDIR /usr/src/app

# Копіюємо dependency-файли
COPY ./poetry.lock ./pyproject.toml ./

# Вимикаємо створення віртуального оточення
RUN poetry config virtualenvs.create false

# Встановлюємо залежності без кешу
RUN poetry install --no-root --only main

# Копіюємо решту коду
COPY ./src ./
COPY ./alembic.ini /usr/src/alembic/alembic.ini
COPY ./commands /commands

# Додаємо права на виконання скриптів
RUN chmod +x /commands/*.sh

# Запускаємо сервер
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
