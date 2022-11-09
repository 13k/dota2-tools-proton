FROM python:3.10-slim-bullseye as build

ARG APP_PATH="/app"
ARG POETRY_HOME="/usr/local/share/pypoetry"

ENV POETRY_HOME="$POETRY_HOME"
ENV PATH="${POETRY_HOME}/bin:${PATH}"
ENV D2TP_BIN="/usr/bin/d2tp"

RUN set -exu \
  && mkdir -p "$APP_PATH"

WORKDIR "$APP_PATH"

RUN set -exu \
  && apt-get update \
  && apt-get -y install --no-install-recommends --no-install-suggests \
    binutils \
    curl \
    upx-ucl \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p "$POETRY_HOME" \
  && curl -sfSL -o "${POETRY_HOME}/install-poetry.py" "https://install.python-poetry.org" \
  && python "${POETRY_HOME}/install-poetry.py" \
  && poetry --version

COPY . "$APP_PATH"

RUN set -exu \
  && bash "${APP_PATH:?}/scripts/build.sh"

FROM debian:bullseye-slim

ENV D2TP_BIN="/usr/bin/d2tp"

COPY --from=build "/usr/bin/d2tp" "${D2TP_BIN:?}"

RUN set -exu \
  && chmod 755 "${D2TP_BIN:?}" \
  && "${D2TP_BIN:?}" --version
