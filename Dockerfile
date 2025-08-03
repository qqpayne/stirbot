# syntax=docker.io/docker/dockerfile:1.7-labs
FROM python:3.10.13-slim-bullseye

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_HOME="/etc/poetry" \
    POETRY_CACHE_DIR="/tmp/poetry_cache" \
    POETRY_VERSION=1.8.3

WORKDIR /app

COPY poetry.lock pyproject.toml .

RUN apt-get update \
    && apt-get install -y curl build-essential libffi-dev libssl-dev python3-dev pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . "$HOME/.cargo/env" \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && poetry install --without dev --no-root \
    && pip install --no-cache-dir greenlet \
    && pip uninstall -y poetry \
    && rm -rf /home/appuser/.cache \
    && rm -rf $POETRY_CACHE_DIR \
    && apt-get purge -y build-essential libffi-dev libssl-dev python3-dev pkg-config \
    && apt-get autoremove -y \
    && rm -rf "$HOME/.cargo" \
    && rm -rf "$HOME/.rustup"

COPY --exclude=poetry.lock --exclude=pyproject.toml . .

RUN adduser --disabled-password appuser && chown -R appuser:appuser .

USER appuser

ENV PATH "/app/scripts:${PATH}"
ENTRYPOINT ["docker-entrypoint.sh"]
