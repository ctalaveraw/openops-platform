# File map

| Path | Purpose |
| --- | --- |
| `Makefile` | Runs the component's offline checks |
| `rules/deployment.py` | Four focused Deployment rules |
| `scripts/evaluate.py` | CLI, structured reports and exit codes |
| `scripts/lint.py` | Python and JSON syntax checks |
| `fixtures/allowed/` | A compliant test Deployment |
| `fixtures/denied/` | Unsafe but parseable Deployments |
| `fixtures/invalid/` | Malformed JSON or unsupported input |
| `tests/test_policy.py` | Positive, negative and read-only tests |
| `docs/POLICY.md` | Rule scope, engine choice and exceptions |
| `docs/CHECKS.md` | Commands, results and recovery |

The JSON fixtures are not used by Hello World at runtime.
The `.json.txt` fixture is intentionally malformed and stays outside generic
JSON lint discovery.
