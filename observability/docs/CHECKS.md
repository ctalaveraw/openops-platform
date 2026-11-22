# Checks

## Tool setup

Proposed promtool version: **3.15.0**, matching the reference ARM Prometheus
image. Source: [Prometheus releases](https://github.com/prometheus/prometheus/releases/tag/v3.15.0).
License: Apache-2.0. Obtain the matching architecture release and verify its
published checksum before placing the binary on PATH. Lane 00 must review
shared bootstrap and CI installation. Python 3.12 is the existing project
runtime. No additional Python packages are needed.

## Commands

Run in this directory after tool setup.

| Command | Expected result |
| --- | --- |
| `make lint` | Prometheus config and rules pass native validation. |
| `make test` | Rule evaluation and payload tests pass. |
| `make test-payloads` | Both Python tests pass. |
| `make prose-check` | Vendored checker accepts each component document. |
| `make check` | All required checks pass without a running service. |

The rule suite uses one-minute sample and evaluation intervals. At minute one
the probe fails. No alert fires until minute three. A good sample at minute
four clears the alert. A short failure never fires. A stale sample produces an
empty recording result and fires after the same hold time.

To exercise a failing assertion, copy this directory to a temporary directory.
Change the alert's hold time from 2m to 20m in the copy. Run its `make test`.
The expected firing case must fail. Remove the copy afterward. The payload
suite also rejects a resolution from another occurrence.

If promtool is missing, lint and check fail. Install the reviewed binary and
rerun the commands. Do not treat a skipped native test as a valid rule result.
If prose fails, repair the named document without changing the checker.

The checks run no network calls. Tool acquisition is a separate setup step.
