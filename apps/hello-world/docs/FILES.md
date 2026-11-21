# File map

Read this table when a file appears unrelated to a single web page.

| File or directory | Why it exists | Check or future integration |
| --- | --- | --- |
| `public/index.html` | Visible anime banner | HTML structure and banner test |
| `public/style.css` | Banner appearance | Local CSS reference test; future CSS lint |
| `public/favicon.svg` | Vector icon | XML parser; future SVG checks |
| `public/site.webmanifest` | Web metadata | JSON parse; URL reference tests |
| `public/robots.txt` | Crawl instructions | Text contract test |
| `public/healthz` | Static HTTP probe | Body test; future HTTP readiness |
| `public/version.txt`, `VERSION` | Version marker | Equality test; future release tagging |
| `fixtures/hello.json` | Reference episode record | Python JSON parsing |
| `fixtures/hello.csv`, `.tsv` | Delimited data | Python CSV parsing and parity |
| `fixtures/hello.xml` | XML specimen | XML parser; XSD schema check |
| `fixtures/hello.yaml` | YAML specimen | Root YAML lint; focused parity check |
| `fixtures/hello.toml` | TOML specimen | Python `tomllib` and parity |
| `fixtures/hello.ini` | INI specimen | Python `configparser` and parity |
| `fixtures/hello.jsonl` | Line-delimited JSON | Python JSON decoding and parity |
| `fixtures/hello.properties` | Key/value specimen | Python parity and duplicate-key check |
| `fixtures/invalid/` | Deliberately broken inputs | Negative tests; not generic lint inputs |
| `fixtures/public.sha256` | Source checksums for the seven served files | Python SHA-256 parity; later artifact integrity |
| `contracts/component.json` | Example child-Make interface | Python target checks; optional JSON Schema |
| `schemas/component.schema.json` | Interface shape | Optional JSON Schema check |
| `docs/MAKE-CONTRACT.md` | Parent/child Make instructions | Example only; no root wiring |
| `schemas/hello.schema.json` | JSON data contract | JSON Schema validator (optional extra check) |
| `schemas/hello.xsd` | XML contract | XSD validator (optional extra check) |
| `schemas/workload.schema.json` | Workload contract | JSON Schema validator (optional extra check) |
| `contracts/workload.yaml` | Example platform input | YAML lint; optional schema validation |
| `contracts/openapi.yaml` | One documented HTTP response | YAML lint; future OpenAPI validator |
| `l10n/en.po` | Gettext sample; not used by the site | Future `msgfmt --check` |
| `fixtures/hello.sql`, `invalid/bad.sql` | One SQLite record and a failure case | In-memory SQL execution; no database file |
| `fixtures/hello.prom`, `invalid/bad.prom` | Sample metrics text and a bad value | Narrow metric format and negative checks; no exporter |
| `fixtures/hello.http` | Two example HTTP requests | Offline path and port checks; no request sent |
| `fixtures/hello.rss.xml` | One unpublished feed item | XML parsing and episode parity |
| `fixtures/hello.env.example` | Harmless configuration sample | Key/value checks; not loaded or sourced |
| `fixtures/hello.log` | One example log record | Timestamp and field checks; not emitted by the app |
| `fixtures/hello.dot` | Planned source-to-image diagram | Optional Graphviz syntax check |
| `.editorconfig`, `.gitattributes` | File editing and line-ending rules | Focused setting checks; scoped to this folder |
| `tests/test_specimens.py` | Tests for the extra specimens | SQL, metrics, feed, HTTP, log, archive round-trip |
| `scripts/verify.py` | Local source/fixture checks | Python unit tests and `make lint` |
| `scripts/check_schemas.py` | Optional full schema check | `make schema-check` |
| `scripts/smoke.sh` | Check a running HTTP server | `sh -n`; manual `make smoke` |
| `tests/` | Verify success and expected failure | Python `unittest`, including Make preview |
| `Dockerfile`, `.dockerignore` | Optional static image | Future image lint/build/inspection |
| `compose.yaml` | Optional local container run | `make compose-check` |
| `Makefile` | Operator entry points | `make help`; `make check`; optional `make prose-check` |

Only `public/` is copied into the image. The other files are exercise material
and remain outside the served web directory.
