# Local fixture commands only. No connection to the platform root Makefile.
.DEFAULT_GOAL := help
SHELL := /bin/sh
PYTHON ?= python3
PORT ?= 8080
IMAGE ?= openops-hello-world:local

.PHONY: help check lint test run smoke compose-check build up down schema-check

help:
	@printf '%s\n' 'make check         Validate files and run unit tests (offline)' 'make run           Serve public/ locally (development only)' 'make smoke         Check a running server on http://127.0.0.1:8080' 'make compose-check Validate optional Compose file (requires Docker)' 'make build         Build local image (requires Docker)' 'make up/down       Start/stop optional Compose service' 'make schema-check  Run full schema checks (optional Python libraries)'

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
