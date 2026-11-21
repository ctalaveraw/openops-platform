# Requires GNU Make, Git, and the uv version in pyproject.toml.
# Run make bootstrap to prepare Python and the locked tooling.

# Running without options shows help by default
.DEFAULT_GOAL := help

# All recipes use /bin/sh declaratively
SHELL := /bin/sh

# Define tasks, .PHONY is used to not collide with files that match task names
.PHONY: help bootstrap setup doctor-python check lint lint-markdown lint-yaml lint-python lint-shell lint-json lint-toml lint-make lint-prose validate-actions

help:
	@echo "setup			Install locked Python tooling"
	@echo "bootstrap		Prepare Python and locked tooling"
	@echo "doctor-python	Check the Python tooling environment"
	@echo "lint-markdown	Check repository Markdown"
	@echo "lint-yaml		Check repository YAML"
	@echo "lint-python		Check Python lint and formatting"
	@echo "lint-json		Check JSON and notification examples"
	@echo "lint-toml		Check TOML and the uv lockfile"
	@echo "lint-shell		Check repository shell scripts"
	@echo "lint-make		Check Makefile source and interfaces"
	@echo "lint-prose		Check documentation prose"
	@echo "validate-actions	Check GitHub Actions workflows"
	@echo "check			Run required checks"

# Prepare the project runtime, then install locked tooling
bootstrap:
	uv python install --no-bin
	$(MAKE) setup

# Install locked Python tooling into this checkout
setup:
	uv sync --locked --no-python-downloads

# Examine Python tooling offline
doctor-python:
	@uv sync --locked --no-python-downloads --offline --check --quiet

# "check" requires source lint and workflow validation
check: lint validate-actions

# "lint" runs the required source checks
lint: lint-markdown lint-yaml lint-python lint-shell lint-json lint-toml lint-make

# "lint-markdown" requires "doctor-python", then runs markdown check
lint-markdown: doctor-python
	@.venv/bin/python scripts/ci/check_markdown.py

# "lint-yaml" requires "doctor-python", then runs YAML check
lint-yaml: doctor-python
	@.venv/bin/python scripts/ci/check_yaml.py

# "lint-python" checks source without applying fixes
lint-python: doctor-python
	@.venv/bin/python scripts/ci/check_python.py

# "lint-shell" checks selected shell source without executing it
lint-shell: doctor-python
	@.venv/bin/python scripts/ci/check_shell.py

# "lint-json" parses JSON and validates notification examples
lint-json: doctor-python
	@.venv/bin/python scripts/ci/check_json.py

# "lint-toml" parses TOML source and the root uv lockfile
lint-toml: doctor-python
	@.venv/bin/python scripts/ci/check_toml.py

# "lint-make" reads Makefile source without running component targets
lint-make: doctor-python
	@.venv/bin/python scripts/ci/check_make.py

# "lint-prose" requires "doctor-python", then runs document prose check
lint-prose: doctor-python
	@.venv/bin/python scripts/ci/check_prose.py

# "validate-actions" checks workflow definitions and embedded shell source
validate-actions: doctor-python
	@.venv/bin/python scripts/ci/validate_actions.py
