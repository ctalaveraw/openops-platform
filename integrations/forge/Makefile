.DEFAULT_GOAL := help
SHELL := /bin/sh
PYTHON ?= python3
.PHONY: help lint test check

help:
	@printf 'lint\tCheck Python syntax and fixture JSON\n'
	@printf 'test\tRun offline adapter tests\n'
	@printf 'check\tRun all required offline checks\n'

lint:
	@$(PYTHON) -B -c 'import ast,json; from pathlib import Path; [ast.parse(p.read_text()) for p in [Path("forge_adapter.py"), *Path("tests").glob("test_*.py")]]; [json.loads(p.read_text()) for p in Path("fixtures").glob("*.json")]; print("Syntax and JSON fixtures: OK")'

test:
	@$(PYTHON) -B -m unittest discover -s tests -v

check: lint test
