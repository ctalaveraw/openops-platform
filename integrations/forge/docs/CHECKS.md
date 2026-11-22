# Forge adapter checks

From `integrations/forge/`, run `make check` using Python 3.12 or newer.
The check does not need GitHub, Forgejo, network, secrets, Docker or a runner.

| Command | Expected result | Failure and recovery |
| --- | --- | --- |
| `make help` | Lists four implemented targets. | Run from the component directory. |
| `make lint` | `Syntax and JSON fixtures: OK`. | Inspect the Python syntax or malformed fixture. |
| `make test` | Offline unit tests pass. | Check the named assertion, fixture and provider mapping. |
| `make check` | Both lint and tests pass. | Fix failing checks; do not bypass them. |

Tests use `unittest.mock` and temporary files for valid and invalid responses,
HTTP errors, timeouts, unexpected status, malformed JSON and oversized responses.
The network helper receives a mock opener. It never performs live requests in
`make check`.

To verify the negative path manually, change a temporary copy of a fixture to
use an incorrect PR number. Running the fixture-preview command with that copy
must exit with status `2`. Restore the fixture; do not edit the checked-in
expected output to conceal a failed check.

The actual GitHub/Forgejo API behavior, authentication, and compatibility with
a running Forgejo instance remain unverified. No root workflow invokes these
component checks yet; root integration is a separate coordination change.
