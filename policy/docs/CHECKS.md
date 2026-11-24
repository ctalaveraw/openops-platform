# Policy checks

Run from `policy/` after Python 3.12+ is available:

```sh
make lint
make test
make check
```

| Command | Expected result | Failure handling |
| --- | --- | --- |
| `make lint` | Parse Python source and valid JSON specimens | Fix malformed component source |
| `make test` | Pass all allowed, denied and invalid-input tests | Check the failing rule or expected status |
| `make check` | Lint and tests pass, offline | Fix the failing child target |

The tests invoke the actual CLI in subprocesses. A clean Deployment returns
exit 0. A policy denial returns 1. A parse, structure, IO or unsupported-kind
error returns 2. A mixed batch containing an error also returns 2.

Use JSON output for machine-readable results:

```sh
python3 scripts/evaluate.py --format json fixtures/allowed/safe.json
```

The report version is `openops-policy-report/v1`. Every entry has `file`,
`status` and `findings`. Denials include stable rule IDs, paths and messages.
Errors include an `error.category` and message. The report prints to stdout.
No report file is written by default. Outputs contain no credentials.

Run the vendored `vendor/slopmonster/deslop.py` on the component docs
from the repository root before review. Record the actual output. Missing
vendored tooling is an unverified check, not a pass.

## Recovery

Inspect the named fixture and the corresponding rule. Fix intended edits
before rerunning `make check`. Do not change exit codes or suppress a finding
to make the suite green. The runner does not need Docker or Kubernetes.
