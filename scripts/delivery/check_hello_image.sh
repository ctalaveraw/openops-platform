#!/bin/sh
# Build and smoke-test one local image. No registry or cluster access.
set -eu

ROOT=$(CDPATH= cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"

image=${IMAGE:-openops-hello-world:ci}
port=${PORT:-18080}
container=""

cleanup() {
    if [ -n "$container" ]; then
        docker rm -f "$container" >/dev/null
    fi
}
trap cleanup EXIT

command -v docker >/dev/null 2>&1 || { echo 'Docker is required.' >&2; exit 2; }
command -v curl >/dev/null 2>&1 || { echo 'curl is required.' >&2; exit 2; }

make -C apps/hello-world compose-check
make -C apps/hello-world build IMAGE="$image"

user=$(docker image inspect --format '{{.Config.User}}' "$image")
case "$user" in
    ""|0|root)
        echo 'FAIL: container must use a non-root user.' >&2
        exit 1
        ;;
esac

container=$(docker run --detach --rm --publish "127.0.0.1:${port}:8080" "$image")
attempt=0
until curl --fail --silent --show-error --max-time 2 "http://127.0.0.1:${port}/healthz" >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 20 ]; then
        docker logs "$container" >&2
        echo 'FAIL: container did not become healthy.' >&2
        exit 1
    fi
    sleep 1
done

make -C apps/hello-world smoke PORT="$port"
docker exec "$container" sh -c 'test ! -e /usr/share/nginx/html/fixtures && test ! -e /usr/share/nginx/html/tests'
echo 'PASS: local image, non-root user, HTTP smoke and image contents'
