# File map and coverage

All files except `public/` are development material. The Dockerfile copies
that directory alone. No additional application service exists.

## Runtime files

| File | Coverage | Local check |
| --- | --- | --- |
| `public/index.html` | Tested | Heading, links, no script or iframe, checksum |
| `public/style.css` | Partial | Linked asset exists, checksum. Root CSS lint |
| `public/favicon.svg` | Partial | SVG root, viewBox, title, checksum |
| `public/site.webmanifest` | Partial | JSON, local start URL, icon, display, checksum |
| `public/robots.txt` | Tested | Exact crawl instructions, checksum |
| `public/healthz` | Tested | Body and checksum |
| `public/version.txt` | Partial | Equals VERSION, checksum |
| `VERSION` | Partial | Three numeric fields, parity |

## Episode and other specimens

| File | Coverage | Local check |
| --- | --- | --- |
| `fixtures/hello.json` | Tested | JSON and parity |
| `fixtures/hello.jsonl` | Tested | Single JSON record and parity |
| `fixtures/hello.csv` | Tested | Columns, one complete row, parity |
| `fixtures/hello.tsv` | Tested | Same as CSV with tab delimiter |
| `fixtures/hello.xml` | Tested | XML fields and parity, optional XSD |
| `fixtures/hello.yaml` | Partial | Three quoted fields and parity, root YAML lint |
| `fixtures/hello.toml` | Tested | TOML and parity |
| `fixtures/hello.ini` | Tested | INI section and parity, duplicate rejection |
| `fixtures/hello.properties` | Tested | Key/value parity, duplicate rejection |
| `fixtures/hello.sql` | Tested | SQLite in memory |
| `fixtures/hello.prom` | Partial | Known metric line, no general grammar check |
| `fixtures/hello.http` | Tested | Request paths and port, no network |
| `fixtures/hello.rss.xml` | Tested | RSS element checks and episode parity |
| `fixtures/hello.env.example` | Tested | Key/value parity, never sourced |
| `fixtures/hello.log` | Tested | Timestamp and sample fields |
| `fixtures/hello.dot` | Partial | Expected graph edges, optional Graphviz |
| `fixtures/public.sha256` | Tested | SHA-256 parity for all served files |
| `l10n/en.po` | Missing | Gettext validation pending |

## Invalid specimens

| File | Coverage | Local check |
| --- | --- | --- |
| `fixtures/invalid/bad.json.txt` | Tested | JSON parser rejects malformed input |
| `fixtures/invalid/bad.xml` | Tested | XML parser rejects malformed input |
| `fixtures/invalid/duplicate.csv` | Tested | Reject repeated rows |
| `fixtures/invalid/bad.sql` | Tested | SQLite rejects missing table |
| `fixtures/invalid/bad.prom` | Tested | Known metric line rejects text value |
| `fixtures/invalid/component.json` | Optional | JSON Schema rejects wrong Make target |

Other negative tests mutate copies in temporary directories.

## Contracts and packaging

| File | Coverage | Local check |
| --- | --- | --- |
| `contracts/component.json` | Tested | Name, paths, port, targets, optional schema |
| `contracts/workload.yaml` | Partial | Metadata parity, optional schema |
| `contracts/openapi.yaml` | Missing | Optional local health contract, not full OpenAPI |
| `schemas/component.schema.json` | Optional | Valid and invalid document checks |
| `schemas/hello.schema.json` | Optional | Syntax and valid/invalid document checks |
| `schemas/workload.schema.json` | Optional | Syntax and valid/invalid document checks |
| `schemas/hello.xsd` | Optional | XML syntax and valid/invalid structure |
| `Dockerfile` | Partial | Source instructions and digest pin, no build |
| `.dockerignore` | Partial | Literal exclusion list, native matching pending |
| `compose.yaml` | Optional | Sample service contract, optional Compose CLI |
| `.editorconfig` | Partial | Selected settings, no editor integration |
| `.gitattributes` | Partial | Git resolves text and LF rules |

The root `.gitignore` is copied into a temporary repository to test generated
paths and confirm application source remains visible to Git. This does not
edit repository-wide rules.

## Checks and guides

| File | Coverage | Local check |
| --- | --- | --- |
| `Makefile` | Tested | Required targets, dry run, root delegation |
| `checks/__main__.py` | Tested | Select static and format validators |
| `checks/validate_svg.py` | Tested | SVG root, viewBox and title |
| `checks/validate_manifest.py` | Tested | Local start URL, display and icon |
| `checks/formats/` | Tested | Nine fixture-format contracts |
| `tests/test_svg.py`, `tests/test_manifest.py` | Tested | Static validator success and failure |
| `tests/test_static_selector.py` | Tested | Static selector behavior |
| `tests/test_format_selector.py` | Tested | Format selection and rejection |
| `tests/test_json.py` and other format tests | Tested | Format-specific success and failure |
| `scripts/verify.py` | Tested | Source and parity checks with invalid examples |
| `scripts/check_schemas.py` | Optional | Schema and YAML contract checks |
| `scripts/smoke.sh` | Partial | Shell syntax. Runtime smoke is opt-in |
| `tests/test_hello.py` | Tested | Data and page tests |
| `tests/test_specimens.py` | Tested | Extra format specimens |
| `tests/test_component.py` | Tested | Make interface and checksums |
| `tests/test_source_mutations.py` | Tested | Temporary source changes and verifier failures |
| `tests/test_git_metadata.py` | Tested | Git ignore and attribute rules in temporary repositories |
| `tests/test_packaging.py` | Tested | Dockerfile and Dockerignore source contracts |
| `README.md` | Optional | Prose checker |
| `docs/FILES.md` | Optional | Prose checker and file inventory |
| `docs/CHECKS.md` | Optional | Prose checker and command review |
| `docs/MAKE-CONTRACT.md` | Optional | Prose checker and Make interface review |

Coverage describes the current validation scope. Tested means the listed
assertion exists. Partial means only some properties are checked.
Optional requires a separate command. Missing means stronger
validation is absent, not that the source file is missing.
The local check column describes intended coverage, not a CI result or a claim
that every grammar and runtime behavior has been tested.
