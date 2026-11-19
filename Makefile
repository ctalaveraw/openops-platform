# Requires GNU Make, Git, Python 3.12, and the uv version in pyproject.toml.
# Run from the repository root, or use make -C /path/to/openops-platform.

# Running without options shows help by default
.DEFAULT_GOAL := help

# All recipes use /bin/sh declaratively
SHELL := /bin/sh

# Define tasks, .PHONY is used to not collide with files that match task names
.PHONY: help setup doctor-python check lint lint-markdown

help:
	@echo "setup			Install locked Python tooling"
	@echo "doctor-python	Check the Python tooling environment"
	@echo "lint-markdown	Check repository Markdown"
	@echo "check				Run required checks"

# Setup a new Python dependency map
setup:
	uv sync --locked --no-python-downloads

# Examine Python tooling offline
doctor-python:
	@uv sync --locked --no-python-downloads --offline --check --quiet

# "check" requires "lint"
check: lint

# "lint" requires "lint-markdown"
lint: lint-markdown

# "lint-markdown" requires "doctor-python", then runs the wrapper script
lint-markdown: doctor-python
	@.venv/bin/python scripts/ci/check_markdown.py
