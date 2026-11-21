# JSON checks

Run `make lint-json`.
The required `make check` gate includes this target.

## Scope

The wrapper selects existing tracked and new nonignored `.json` files.
Vendor metadata is included. Tracked deletions are skipped.
An empty selection fails.

Each file must contain one UTF-8 JSON document.
Duplicate keys are rejected at every nesting level.
Bare `NaN` and `Infinity` are rejected. This includes negative infinity.
The check reads source without rewriting it.

## Notification examples

JSON under `examples/notifications/` also uses the notifier's `read_event` validator.
That applies the existing size limit and field checks.
It reads event data without sending notifications.

Other JSON receives parsing and duplicate-key checks.
Future data contracts need an explicit validator mapping.

## Setup and execution

Run `make bootstrap`.
The check uses the standard library and the existing event validator.
It adds no dependencies.
Paths come from the wrapper's location.
The checkout root is added to this process's import path.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | Every selected file passed. |
| `1` | A file failed parsing or the notification event contract. |
| `2` | Setup failed or a file could not be read. |

These are wrapper statuses. GNU Make reports a failed recipe with its own
nonzero exit status.
