.DEFAULT_GOAL := help
SHELL := /bin/sh
ROOT := $(abspath ../..)
PYTHON ?= $(ROOT)/.venv/bin/python

.PHONY: help lint test check preview prose-check

help:
	@echo "lint         Check notifier Python with locked Ruff"
	@echo "test         Run offline notifier and routing tests"
	@echo "prose-check  Check component and notifier documentation"
	@echo "check        Run lint, tests and prose checks"
	@echo "preview      Print a synthetic PR routing proposal"

lint:
	$(PYTHON) -m ruff check --no-cache --config $(ROOT)/pyproject.toml $(ROOT)/scripts/notifications $(ROOT)/tests/notifications
	$(PYTHON) -m ruff format --check --no-cache --config $(ROOT)/pyproject.toml $(ROOT)/scripts/notifications $(ROOT)/tests/notifications

test:
	cd $(ROOT) && $(PYTHON) -B -m unittest discover -s tests/notifications -v

prose-check:
	cd $(ROOT) && $(PYTHON) -B -c 'from scripts.ci.check_prose import verify_vendor; verify_vendor()'
	cd $(ROOT) && for file in integrations/chatops/README.md integrations/chatops/docs/FILES.md integrations/chatops/docs/CHECKS.md docs/ci/zulip-notifications.md; do $(PYTHON) -B vendor/slopmonster/deslop.py "$$file" || exit 1; done

check: lint test prose-check

preview:
	$(PYTHON) -B $(ROOT)/scripts/notifications/preview_route.py --event $(ROOT)/examples/notifications/github-failure.json --pull-request 123
