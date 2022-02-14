FROM python:3.9-slim-buster

ARG D2TP_VERSION
ARG \
  APP_PATH="/app" \
  POETRY_HOME="/usr/local/share/pypoetry"

ENV POETRY_HOME="$POETRY_HOME"
ENV PATH="${POETRY_HOME}/bin:${PATH}"
ENV \
  D2TP_VERSION="$D2TP_VERSION" \
  D2TP_BIN="d2tp"

WORKDIR "$APP_PATH"

RUN set -exu \
  && apt-get update \
  && apt-get -y install --no-install-recommends --no-install-suggests \
  curl \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p "$POETRY_HOME" \
  && curl -sfSL -o "${POETRY_HOME}/install-poetry.py" "https://install.python-poetry.org" \
  && python "${POETRY_HOME}/install-poetry.py" \
  && poetry --version

COPY "poetry.lock" "pyproject.toml" ./
COPY "d2tp" ./d2tp

RUN set -exu \
  && poetry build \
  && python -m pip install --disable-pip-version-check --no-cache-dir "dist/dota2_tools_proton-${D2TP_VERSION}-py3-none-any.whl" \
  && "$D2TP_BIN" --version
