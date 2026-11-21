#!/bin/sh
# Explicit opt-in HTTP check. Run only after starting a server.
set -eu

base_url=${1:-http://127.0.0.1:8080}
html=$(curl --fail --silent --show-error --max-time 5 "$base_url/")
health=$(curl --fail --silent --show-error --max-time 5 "$base_url/healthz")
css=$(curl --fail --silent --show-error --max-time 5 "$base_url/style.css")
missing=$(curl --silent --show-error --max-time 5 --output /dev/null --write-out '%{http_code}' "$base_url/not-found")

printf '%s\n' "$html" | grep -Fq 'Hello, Ops World!'
printf '%s\n' "$css" | grep -Fq '.banner'
[ "$health" = 'ok' ]
[ "$missing" = '404' ]
printf '%s\n' 'PASS: banner, CSS, health and missing-file response'
