# Forge adapter file inventory

| Path | Purpose |
| --- | --- |
| `forge_adapter.py` | Validate provider inputs, normalize PR responses and optionally fetch a public PR with read-only GET. |
| `fixtures/github-pr.json` | Synthetic GitHub API response for PR #17. |
| `fixtures/forgejo-pr.json` | Synthetic Forgejo API response for PR #31. |
| `fixtures/expected-github.json` | Exact expected normalized GitHub result. |
| `fixtures/expected-forgejo.json` | Exact expected normalized Forgejo result. |
| `tests/test_forge_adapter.py` | Positive/negative fixtures and mocked HTTP behavior. |
| `Makefile` | Independent offline `help`, `lint`, `test`, and `check` commands. |
| `docs/CAPABILITIES.md` | Native/adapter/gap inventory, scope status and cross-lane questions. |
| `docs/CHECKS.md` | Commands, expected results and troubleshooting. |
| `README.md` | Purpose, interface, usage, limits, and integration boundaries. |

The shared OpenOps event schema, notifications, root CI, root dependency lock,
and live Forgejo configuration belong to other workstreams.
