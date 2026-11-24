# Checks and troubleshooting

Run commands from `apps/hello-world/` in a full OpenOps checkout.

| Command | Needs | Expected result |
| --- | --- | --- |
| `make check` | Python, Make, shell, Git | Source checks and unit tests pass |
| `make lint` | Python and shell | Script syntax and fixture parity pass |
| `make check-static CASE=svg` | Python | Validate one static asset contract |
| `make check-formats CASE=csv` | Python | Validate one fixture format |
| `make test` | Python, Make, Git | Unit tests pass |
| `make schema-check` | Optional Python libraries | Good schemas pass, invalid documents fail |
| `make prose-check` | Vendored SlopMonster | Each guide and banner scores 5/5 |
| `make diagram-check` | Graphviz | DOT file parses |
| `make compose-check` | Compose CLI | Resolved Compose model is valid |
| `make run` | Python | Local development server starts |
| `make smoke` | Running server and curl | Banner, CSS, health and 404 pass |
| `make build` | Docker daemon | Local image builds |
| `make up` / `make down` | Docker daemon | Local service starts or stops |

Python 3.11 or newer is needed for the local standard library checks. Use the
repository's pinned Python for CI parity. The default check makes no network
requests and starts no services. Git tests use temporary repositories.

The schema check uses `jsonschema`, `PyYAML` and `lxml`. It checks all three
JSON schemas and the XSD with accepted and rejected documents. The YAML
checks compare the Compose service and the OpenAPI health path against this
fixture. They do not replace the native Compose or OpenAPI validators.

The SQL example executes in memory. Metrics, RSS, request, environment and
log examples are read as test data. The metrics check covers the sample line,
not the full Prometheus grammar. The Dockerfile test checks its four source
instructions. The exclusion-list test does not evaluate Docker's matching
rules. No image is built by the required check.

## Expected failures

The unit tests modify temporary copies or use the committed invalid examples.

- Wrong CSV contents fail parity. Missing fields fail the CSV loader.
- Duplicate INI or properties keys fail parsing.
- Missing page assets or external manifest URLs fail the static check.
- An invalid SVG root or invalid matching version strings fail the static check.
- A changed served file fails its committed checksum.
- Source paths excluded by Git fail the ignore-rule test.
- A Dockerfile that copies the whole directory fails its source contract.
- The optional schema checker rejects incomplete XML and invalid JSON records.

Run `make test` to identify the failing assertion. Run `make lint` if the source
verifier reports a failure. Restore unintended changes before retrying. For
an intended served-file change, regenerate the manifest with
`sha256sum public/* > fixtures/public.sha256` and review the diff. Checksums
catch accidental drift, not a malicious edit to both files.

The malformed JSON in `fixtures/invalid/bad.json.txt` has a text suffix so
repository-wide JSON lint does not reject a deliberate test input.

## Deferred checks

Native Gettext validation, Dockerignore matching and full OpenAPI lint need
reviewed tooling. Hadolint and the Compose CLI are separate checks. Repository-wide validators are maintained at the repository root. No local port,
registry or cluster is needed to complete this work.

Root `make check-apps` delegates to the child. The existing image workflow
is separate from that command. Do not publish or deploy during offline work.
See [the Make contract](MAKE-CONTRACT.md) and [file coverage](FILES.md).
