# Local fixture commands only. No connection to the platform root Makefile.
.DEFAULT_GOAL := help
SHELL := /bin/sh
PYTHON ?= python3
PORT ?= 8080
IMAGE ?= openops-hello-world:local

.PHONY: help check lint test run smoke compose-check build up down schema-check prose-check diagram-check

help:
	@printf '%s\n' \
		'make check         Run offline checks and unit tests' \
		'make run           Serve public/ locally (development only)' \
		'make smoke         Check a running server on PORT (default: 8080)' \
		'make compose-check Validate Compose without starting containers' \
		'make build         Build local image (requires Docker)' \
		'make up/down       Start or stop optional Compose service' \
		'make schema-check  Validate schemas (optional Python libraries)' \
		'make diagram-check Validate example DOT graph (optional Graphviz)' \
		'make prose-check   Run vendored SlopMonster on docs and banner'

check: lint test

lint:
	@$(PYTHON) -m compileall -q scripts tests
	@sh -n scripts/smoke.sh
	@$(PYTHON) scripts/verify.py

test:
	@$(PYTHON) -m unittest discover -s tests -v

run:
	@$(PYTHON) -m http.server $(PORT) --bind 127.0.0.1 --directory public

smoke:
	@sh scripts/smoke.sh http://127.0.0.1:$(PORT)

compose-check:
	@docker compose -f compose.yaml config --quiet

build:
	@docker build -t $(IMAGE) .

up:
	@docker compose -f compose.yaml up -d --build

down:
	@docker compose -f compose.yaml down

schema-check:
	@$(PYTHON) scripts/check_schemas.py

# Existing OpenOps tool, optional until the platform enables this application.
prose-check:
	@test -f ../../vendor/slopmonster/deslop.py || { echo 'SlopMonster is missing; run from an OpenOps checkout.' >&2; exit 2; }
	@for path in README.md docs/FILES.md docs/CHECKS.md docs/MAKE-CONTRACT.md public/index.html; do \
		$(PYTHON) ../../vendor/slopmonster/deslop.py "$$path" || exit $$?; \
	done

# Optional graph parser; no generated or tracked artifact.
diagram-check:
	@command -v dot >/dev/null 2>&1 || { echo 'Graphviz dot is required.' >&2; exit 2; }
	@dot -Tsvg fixtures/hello.dot -o /dev/null
