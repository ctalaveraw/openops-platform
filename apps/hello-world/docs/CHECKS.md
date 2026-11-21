# Checks and troubleshooting

Run these commands from `apps/hello-world/`.

| Command | Does it need a container? | What it checks |
| --- | --- | --- |
| `make check` | No | Python/shell syntax, fixture parity, Make target preview, source checksums, negative tests |
| `make test` | No | Python unit tests only |
| `make lint` | No | Script syntax and source/fixture validation |
| `make run` | No | Local HTTP server; runs until Ctrl+C |
| `make smoke` | Running HTTP server | Banner, CSS, `/healthz` and expected 404 |
| `make schema-check` | No | Full JSON Schema, YAML and XSD with optional Python packages |
| `make prose-check` | No | README, file map, check notes and banner with vendored SlopMonster |
| `make diagram-check` | Graphviz (optional) | Parse sample DOT graph; does not deploy or generate tracked files |
| `make compose-check` | Docker CLI | Compose file structure; does not start services |
| `make build` | Docker daemon | OCI image build; manual only |
| `make up` / `make down` | Docker daemon | Start/stop demo container; manual only |

`make check` requires Python 3.11 or newer for `tomllib`. It makes no network
requests and does not start the container. The optional schema check requires
`jsonschema`, `PyYAML`, and `lxml` in the Python environment. The prose check
uses the pinned script at `../../vendor/slopmonster/deslop.py` in the full
OpenOps checkout. Neither optional check runs under `make check`. A missing
optional tool causes a clear error; the default check does not depend on them.

The component tests use `make -n` to preview child targets without running
them. They check that the component metadata matches the existing workload
contract. They also compare committed SHA-256 sums with the served files.
The extra fixture tests parse SQL in an in-memory SQLite database and inspect a
Prometheus text sample, HTTP request examples, an RSS item, a sample environment
file and one log line. They also check line-ending rules and archive round trips.
No database, metrics endpoint, feed or config loader is started.
The metrics check covers this one known example, not the full Prometheus grammar.

`make diagram-check` is a separate, opt-in Graphviz check. It requires `dot`
and runs no image build or deployment.

## Expected failures

- Modify one CSV title: the parity check reports which format disagrees.
- Add a second CSV row with the same ID: validation rejects duplicate IDs.
- Break JSON or XML syntax: the negative tests demonstrate rejection.
- Change the banner heading: the static asset test fails.
- Change the metric value to a word: the metrics test fails.
- Break the SQL table name: the SQLite test fails.
- Stop the server, then run `make smoke`: the shell command fails.
- Edit `public/style.css`: the SHA-256 check fails until the manifest is updated.

After an intended change to a served file, regenerate its committed digest from
this directory with `sha256sum public/* > fixtures/public.sha256` (GNU coreutils).
Review the diff; do not accept unrelated content changes. This catches accidental
source changes, not malicious edits to both files. The local `.gitattributes`
keeps served text files at LF line endings on different operating systems.

Restore the fixture after each experiment. Broken inputs in
`fixtures/invalid/` are intentional; tests check that they are rejected.

## What has not been exercised

This directory is not wired into the root Makefile or CI. The Docker and Compose
commands are optional and require a container engine. There is no registry
publication, deployment, GitOps manifest, external webhook, or alert.

When the platform is ready, add one integration at a time and link to a real
command or test result. Do not mark a check as working because its file exists.

[Parent/child Make contract](MAKE-CONTRACT.md) explains how the platform may
invoke this component later without importing its code.
