# Makefile checks

Run `make lint-make`.
The required `make check` gate includes this target.

## Scope

The wrapper selects existing tracked and new nonignored Makefiles.
Names are `Makefile`, `makefile` and `GNUmakefile`.
It also selects `.mk` and `.make` fragments.
Files under the root `vendor/` directory are excluded.
Tracked deletions are skipped. The root `Makefile` is required.

## Public interface

Each standalone Makefile declares literal, unconditional `help:` and `check:` targets.
Both targets are declared in `.PHONY`.
The help recipe's source must mention the `check` command.
Fragments receive source parsing without this interface requirement.

## Component ownership

The root gate reads discovered component Makefiles as source.
Each component owns what its `check` target runs.
Adding a Makefile does not activate that component's tests or builds.
Root delegation requires a separate change.

## Parser and limits

`tree-sitter==0.26.1` supplies the parsing engine.
`tree-sitter-make==1.1.1` supplies the Make grammar.
Run `make setup` to install them from `uv.lock`.

The wrapper builds syntax trees and leaves recipe text unevaluated.
Includes are not followed. Variables are not expanded.
The parser accepts a subset of GNU Make syntax.
Custom `.RECIPEPREFIX` requires a parser review.
The grammar also lacks support for the `load` directive.

GNU Make remains the execution authority.
Passing this check establishes source structure and the declared interface.
Command behavior needs separate execution tests owned by the component.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | Every selected file passed. |
| `1` | Source or interface findings were reported. |
| `2` | Setup failed or a file could not be read. |

These are wrapper statuses. GNU Make reports a failed recipe with its own
nonzero exit status.
