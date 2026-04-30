FROM python:3.11-slim AS base

WORKDIR /app

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# ── Production image ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

COPY --from=base /app/.venv ./.venv
COPY app ./app

ENV PATH="/app/.venv/bin:$PATH" \
    APP_ENV=production \
    DEBUG=false

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
