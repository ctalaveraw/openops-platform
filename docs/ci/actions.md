# Actions validation

Run `make validate-actions` from the repository root.
The required `make check` gate includes this target.

## Setup

Run `make bootstrap` to install the locked tooling.
The `actionlint-py==1.7.12.25` package installs actionlint 1.7.12.
Its build downloads a checksummed upstream binary from GitHub.
A fresh installation therefore needs build dependencies and GitHub access.

Linux x86_64 installation is verified.
This package has a Linux ARM64 installation route, which remains untested here.
The package does not provide a Linux ARM32 route.

## Scope

The wrapper discovers existing tracked files and new nonignored files directly
inside `.github/workflows/`. It selects `.yml` and `.yaml` files.
Tracked deletions are skipped.
An empty workflow selection fails because this repository must contain workflows.

The checkout root comes from the wrapper's location.
Native tool paths come from the Python interpreter's directory.

## Behavior

YAML lint checks document syntax and style.
actionlint also checks workflow structure and expression types.
It validates job references and recognized action inputs.

The wrapper explicitly loads `.github/actionlint.yaml`.
The initial configuration is an empty mapping.

Inline shell commands are analyzed by the pinned ShellCheck binary.
The wrapper checks that ShellCheck can execute before invoking actionlint.
It sets `SHELLCHECK_OPTS=--norc` so user configuration cannot suppress findings.
The optional Pyflakes integration is disabled.
Keep Python program logic in repository files checked by Ruff.

Validation reads workflow source without running jobs or rewriting files.
These GitHub workflow checks can run locally or on another provider's runner.
Forgejo-specific workflow validation is separate work.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | The selected workflows passed. |
| `1` | actionlint reported findings. |
| `2` | Setup or discovery failed, or a tool could not complete. |

These are wrapper statuses. GNU Make reports a failed recipe with its own
nonzero exit status.
