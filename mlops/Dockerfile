FROM python:3.11-buster as build

RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev && rm -rf $POETRY_CACHE_DIR

# Multi-stage build to reduce image size
FROM quay.io/jupyter/scipy-notebook:latest as run

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY --from=build ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . .

# install nltk data
RUN chmod +x /app/setup.sh && /app/setup.sh

CMD ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:5001", "--log-level", "debug"]
