# TOML checks

Run `make lint-toml`.
The required `make check` gate includes this target.

## Scope

The wrapper selects existing tracked and new nonignored `.toml` files.
The root `uv.lock` is included because it also uses TOML.
Vendor TOML is included. Tracked deletions are skipped.
An empty selection fails.

## Parser

Python 3.12's `tomllib` checks TOML 1.0 syntax.
Duplicate keys fail. Files must use UTF-8.
Empty and comment-only documents are valid TOML.
The check reads source without rewriting it.

Each tool validates the meaning of its own configuration.
The `doctor-python` prerequisite checks the locked tooling environment.

## Setup and execution

Run `make bootstrap`.
The parser is part of Python's standard library and adds no dependencies.
Paths come from the wrapper's location.
Git discovery runs from the checkout root.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | Every selected file passed. |
| `1` | A file failed parsing. |
| `2` | Setup failed or a file could not be read. |

These are wrapper statuses. GNU Make reports a failed recipe with its own
nonzero exit status.
