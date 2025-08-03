#!/usr/bin/env bash

set -euo pipefail

python -m app.utils.prestart

if [ "${DO_MIGRATE}" = true ]; then
  alembic upgrade head
fi

exec python -m app
