FROM quay.io/jupyter/scipy-notebook:latest

RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev && rm -rf $POETRY_CACHE_DIR

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN mkdir /app/mlops
COPY . ./mlops

# install nltk data
RUN poetry run /bin/sh /app/mlops/setup.sh

USER root
# See: https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html#notebook-user
RUN chown -R jovyan:users /app/mlops
USER 1000

# Run forever (the HTTP server should be started by exec_run)
CMD [ "sleep", "infinity" ]
#CMD ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:5001", "--log-level", "debug"]
