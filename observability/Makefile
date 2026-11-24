.DEFAULT_GOAL := help
SHELL := /bin/sh
PROMTOOL ?= promtool
PYTHON ?= python3

.PHONY: help lint test check require-promtool test-payloads prose-check

help:
	@echo "lint          Validate Prometheus config and rules (promtool)"
	@echo "test          Run synthetic rule and alert payload tests"
	@echo "test-payloads Run alert payload tests without promtool"
	@echo "prose-check   Check component Markdown (vendored SlopMonster)"
	@echo "check         Run all required offline checks"

require-promtool:
	@command -v "$(PROMTOOL)" >/dev/null || { echo "Install promtool first; see docs/CHECKS.md" >&2; exit 2; }

lint: require-promtool
	@"$(PROMTOOL)" check config prometheus.yml
	@"$(PROMTOOL)" check rules rules/availability.yml

test: require-promtool test-payloads
	@"$(PROMTOOL)" test rules tests/availability.yml

test-payloads:
	@"$(PYTHON)" -B -m unittest discover -s tests -v

prose-check:
	@for doc in README.md docs/*.md; do "$(PYTHON)" ../vendor/slopmonster/deslop.py "$$doc" || exit; done

check: lint test prose-check
