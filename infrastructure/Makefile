.DEFAULT_GOAL := help
SHELL := /bin/sh
TOFU ?= tofu
PYTHON ?= python3
MODULE := terraform/modules/inventory

.PHONY: help init lint validate test prose-check check

help:
	@echo 'init        Initialize the local module (no external providers)'
	@echo 'lint        Check HCL formatting'
	@echo 'validate    Validate module configuration'
	@echo 'test        Run native plan-only tests'
	@echo 'prose-check Check component documentation'
	@echo 'check       Run all required offline checks'

init:
	$(TOFU) -chdir=$(MODULE) init -backend=false -input=false -no-color

lint:
	$(TOFU) fmt -check -diff -recursive terraform

validate:
	$(TOFU) -chdir=$(MODULE) validate -no-color

test:
	$(TOFU) -chdir=$(MODULE) test -no-color

prose-check:
	@set -e; for path in README.md docs/FILES.md docs/CHECKS.md; do \
		$(PYTHON) ../vendor/slopmonster/deslop.py "$$path"; \
	done

check: lint validate test prose-check
