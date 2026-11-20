# YAML check

Run `make lint-yaml` from the repository root.
The required `make check` gate includes this check.

## Setup

Run `make bootstrap` to prepare Python and the locked tooling.
The checker version is pinned in `pyproject.toml` and resolved in `uv.lock`.

## Scope

The wrapper asks Git for tracked files and new files that Git does not ignore.
It selects existing files with a `.yaml` or `.yml` suffix outside `vendor/`.
Deleted files are skipped.

The script derives the repository root from its own location.
It invokes yamllint through the Python interpreter that launched the wrapper,
using the repository's `.yamllint.yaml` configuration.

## Behavior

Strict mode makes warnings fail the check.
The checker reads files and reports findings without rewriting them.
Actions workflow validation will be handled by a separate check.

## Exit status

- `0`: no findings.
- `1`: yamllint reported errors or warnings.
- `2`: wrapper setup or execution failed.

The wrapper maps yamllint's error and warning exit codes to `1`.
Read the diagnostic output to identify the cause.
