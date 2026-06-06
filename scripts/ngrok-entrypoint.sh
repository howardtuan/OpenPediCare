#!/usr/bin/env sh
set -eu

if [ -n "${NGROK_DOMAIN:-}" ]; then
  exec ngrok http --url "$NGROK_DOMAIN" http://web:8000
fi

exec ngrok http http://web:8000
