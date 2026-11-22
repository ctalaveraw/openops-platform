# ChatOps checks

Run `make bootstrap` from the repository root before checking. The component uses
the existing Python 3.12 environment and locked Ruff 0.17.6. Checks need no bot
configuration or network after bootstrap. To select another prepared environment,
pass an absolute interpreter path as `PYTHON=/path/to/python`.

| Command from repository root | Expected result |
| --- | --- |
| `make -C integrations/chatops help` | Lists lint, test, prose-check, check and preview |
| `make -C integrations/chatops lint` | Ruff lint and format checks pass |
| `make -C integrations/chatops test` | 39 tests pass with in-memory HTTP responses |
| `make -C integrations/chatops prose-check` | Vendored checker passes on all four named guides |
| `make -C integrations/chatops check` | Lint, tests and prose checks return zero |
| `make -C integrations/chatops preview` | Prints the synthetic GitHub PR topic and message |

Tests compare both legacy fixtures and preserve default routing. Routing cases
distinguish providers and group a failure with its recovery. Invalid events and
nested duplicate fields must fail. Message labels exercise Markdown delimiters.
Configuration cases reject organization/channel mismatches. Mock HTTP responses
exercise 401/403 rejection and bounded rate limits. Redirects are refused.
Unavailable servers, response-read failures and ambiguous acknowledgements stop
without resending.
Repeated explicit submissions demonstrate the absence of durable deduplication.

For a manual negative routing check:

```sh
.venv/bin/python -B scripts/notifications/preview_route.py \
  --event examples/notifications/github-failure.json --pull-request 0
```

Expect exit 2, an input error on stderr and no JSON on stdout. Retry with `123`
to restore a successful preview. Adding `--send` must also return exit 2.
Neither command reads credentials or constructs a transport.

Missing tooling must fail the check. Restore the locked environment with
`make bootstrap`. Fix source or assertion failures before retrying. Do not edit
the vendored checker or bypass a failed target. The component never calls the
root `check` and does not run the separate Gotify adapter.

These checks do not prove Zulip rendering, live permissions, topic navigation,
trusted workflow result preservation or delivery/replay acceptance. Those need
separate reviewed activation. Root integration and path migration belong to
lane 00.
