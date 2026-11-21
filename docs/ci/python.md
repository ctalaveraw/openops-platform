# Python checks

Run `make lint-python` from the repository root.
The required `make check` gate includes this check.

## Setup

Run `make bootstrap` to prepare Python and the locked tooling.
Ruff is pinned in `pyproject.toml` and resolved in `uv.lock`.

## Scope

The wrapper selects existing tracked files and new files that Git does not ignore.
It checks `.py` and `.pyi` files outside `vendor/`.
Deleted tracked files are skipped.

The wrapper derives the checkout root from its own location.
Both Ruff commands use the same Python interpreter that launched the wrapper
and load the checkout's `pyproject.toml` explicitly.

## Behavior

The linter reports violations of the configured rules.
The formatter verifies code layout using `--check`.
Both commands run on the selected files without rewriting Python source.
The selected Python programs are not executed.

Ordinary lint findings do not prevent the formatting check from running.

## Fix formatting locally

For the CI wrappers, run:

```sh
.venv/bin/python -m ruff format --no-cache scripts/ci
```

Then rerun `make lint-python`.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | Both Ruff checks passed. |
| `1` | Lint or formatting findings need attention. |
| `2` | Setup failed or a tool could not complete the check. |

These are the wrapper's exit codes. GNU Make reports a failed recipe with its own
nonzero exit status.
