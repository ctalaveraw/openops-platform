.DEFAULT_GOAL := help
SHELL := /bin/sh
PYTHON ?= ../.venv/bin/python
ANSIBLE_PLAYBOOK ?= ../.venv/bin/ansible-playbook

.PHONY: help lint syntax test prose-check check
help:
	@echo 'lint         Check YAML and Python source'
	@echo 'syntax       Parse the local fixture playbook with Ansible'
	@echo 'test         Run template and inventory tests'
	@echo 'prose-check  Check component documentation'
	@echo 'check        Run all required offline checks'

lint:
	$(PYTHON) -m yamllint --strict -c ../.yamllint.yaml ansible
	$(PYTHON) -m ruff check tests
	$(PYTHON) -m ruff format --check tests

syntax:
	ANSIBLE_CONFIG=$(CURDIR)/ansible/ansible.cfg $(ANSIBLE_PLAYBOOK) -i ansible/inventory/fixture.yml --syntax-check ansible/playbooks/baseline.yml

test:
	$(PYTHON) -B -m unittest discover -s tests -v

prose-check:
	@set -e; for file in README.md docs/FILES.md docs/CHECKS.md; do $(PYTHON) ../vendor/slopmonster/deslop.py "$$file"; done

check: lint syntax test prose-check
