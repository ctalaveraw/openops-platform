# Prose check

Run `make lint-prose` to check English prose in `README.md` and Markdown
files under `docs/`. The check includes tracked files and new files that Git
does not ignore. Files outside that scope are excluded.

## Setup

Run `make bootstrap` to prepare Python and the locked tooling environment.
SlopMonster uses Python's standard library and adds no package dependencies.

## Behavior

The wrapper verifies the vendored checker and license against the SHA-256 values
in `vendor/slopmonster/UPSTREAM.json`. It then runs the checker once per file,
using the same Python interpreter that launched the wrapper.

The check reads source files and prints findings. It makes no network requests
and does not rewrite documentation.

## Exit status

- `0`: every selected file passed.
- `1`: at least one scan returned nonzero; read the checker output for the cause.
- `2`: wrapper setup, integrity verification or file discovery failed.

Empty prose fails the check. SlopMonster uses the same exit code for findings
and empty input, so the diagnostic output matters.

## Review

SlopMonster uses English pattern matching. A score of 5/5 means no scored
patterns matched. It does not establish factual accuracy or authorship.
Review findings for context and keep the intended meaning when editing.

This target is optional during evaluation.
`make check` requires the Markdown and YAML checks.
Python linting and formatting are also required.
