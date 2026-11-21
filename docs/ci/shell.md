# Shell checks

Run `make lint-shell` from the repository root.
The required `make check` gate includes this target.

## Setup

Run `make bootstrap` to prepare Python and the locked tooling.
The pinned `shellcheck-py==0.11.0.1` package installs ShellCheck 0.11.0.
The wrapper uses the binary beside its Python interpreter.

The Linux x86_64 installation has been verified.
On Linux ARM, the package builds a wheel by downloading a checksummed upstream
binary. That route needs build dependencies and access to GitHub.
ARM execution remains unverified.

## Scope

The wrapper selects tracked files and new files that Git does not ignore.
It skips deleted files and the root `vendor/` directory.

These suffixes identify shell inputs:

```text
.sh
.bash
.bats
.dash
.ksh
```

Extensionless files are also checked when their shebang names a supported shell.
The wrapper recognizes direct interpreter paths and common `env` forms.
It supports `env -S` and `busybox sh`.
The `SHELL_NAMES` constant lists the other recognized interpreters.

Each selected file must identify its shell through a shebang or a ShellCheck
directive. The wrapper lets ShellCheck choose the dialect for each file.

## Behavior

ShellCheck reads source without executing the selected programs or rewriting them.
All standard finding severities are enabled.
The wrapper ignores `SHELLCHECK_OPTS` and automatic `.shellcheckrc` discovery.
Its command options define the repository policy.

An empty selection prints `SKIP lint-shell` and returns success.
This is expected while the repository has no shell scripts.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | Selected scripts passed, or an explicit empty-scope skip was reported. |
| `1` | ShellCheck reported findings. |
| `2` | Tool setup or file discovery failed, or ShellCheck could not complete. |

These are the wrapper's exit codes. GNU Make reports a failed recipe with its own
nonzero exit status.
