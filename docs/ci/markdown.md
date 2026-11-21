# Markdown check

## Purpose

Run `make lint-markdown` to check repository Markdown before review.
The required `make check` gate includes this check.

## Setup

Use Git, GNU Make, and uv 0.13.9.
Run `make bootstrap` to install the Python version selected by `.python-version`,
then the tools recorded in `uv.lock`.
Python and package downloads can require network access.
Use `make setup` to sync the locked tools when Python is already available.

## Scope

The checker scans this checkout recursively for `.md` files.
It includes new files and applies Git ignore rules.
Virtual environments and generated output are ignored through `.gitignore`.

The script derives the repository root from its own location and invokes
PyMarkdown through the same Python interpreter that launched the script.

## Rules and failures

`.pymarkdown.json` contains repository rules.
MD013 is disabled because long paragraphs and URLs do not require hard wrapping.
Other rules retain their pinned tool defaults.

The explicit return-code scheme distinguishes rule findings from an empty scope.
A finding or execution error exits nonzero and stops the required gate.
The checker does not edit files or install dependencies.
It checks Markdown structure and style; link targets and prose quality have
separate checks.

## Reproduce

Run `make lint-markdown` from the repository root.
For a focused run, use
`.venv/bin/python -m pymarkdown --return-code-scheme explicit --strict-config --config .pymarkdown.json scan README.md`.
