FROM python:3.9-slim-buster

ARG BUILD_PATH="/app"

ENV POETRY_HOME="/usr/local/share/pypoetry"
ENV PATH="${POETRY_HOME}/bin:${PATH}"
ENV D2TP_VERSION="0.1.0"
ENV D2TP_BIN="d2tp"

WORKDIR "$BUILD_PATH"

RUN set -eux ; \
  apt-get update ; \
  apt-get -y install --no-install-recommends --no-install-suggests curl ; \
  rm -rf /var/lib/apt/lists/* ; \
  mkdir -p "$POETRY_HOME" ; \
  curl -sfSL -o "${POETRY_HOME}/install-poetry.py" "https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py" ; \
  python "${POETRY_HOME}/install-poetry.py" ; \
  poetry --version

COPY "poetry.lock" \
  "pyproject.toml" \
  ./

COPY "d2tp" ./d2tp

RUN set -eux ; \
  poetry build ; \
  python -m pip install --disable-pip-version-check --no-cache-dir "dist/dota2_tools_proton-${D2TP_VERSION}-py3-none-any.whl" ; \
  "${D2TP_BIN}" --version
