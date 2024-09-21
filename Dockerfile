FROM python:3.10-slim

# Install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

COPY . .

# Make the script executable
# RUN chmod +x postgres/docker-entrypoint-initdb.d/*.sql

CMD ["poetry", "run", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
