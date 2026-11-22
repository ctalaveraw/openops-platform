# No cluster, registry, image build or network access.
.DEFAULT_GOAL := help
SHELL := /bin/sh
PYTHON ?= python3
.PHONY: help lint test check

help:
	@echo 'lint    Parse policy Python and JSON files without side effects'
	@echo 'test    Run allowed, denied and invalid-manifest tests'
	@echo 'check   Run lint and tests locally, offline'

lint:
	@PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/lint.py

test:
	@PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -v

check: lint test
