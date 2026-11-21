#!/bin/sh
# Explicit opt-in HTTP check. Run only after starting a server.
set -eu

base_url=${1:-http://127.0.0.1:8080}
html=$(curl --fail --silent --show-error --max-time 5 "$base_url/")
health=$(curl --fail --silent --show-error --max-time 5 "$base_url/healthz")

printf '%s\n' "$html" | grep -Fq 'Hello, Ops World!'
[ "$health" = 'ok' ]
printf '%s\n' 'PASS: banner and health endpoint'
