# Zulip CI notifications

Status: the local command and offline tests are implemented. Connecting the
GitHub Actions workflow is follow-up work in [#65](https://github.com/ctalaveraw/openops-platform/issues/65).
The native GitHub integration continues to deliver PR, review and issue activity.

The command uses Python's standard library. It reads a small event file, validates
the fields and formats a compact Zulip message. Preview is the default mode.
Sending requires the explicit `--send` flag and a private bot configuration.

## Preview locally

From the repository root:

```sh
make bootstrap
.venv/bin/python scripts/notifications/notify_zulip.py \
  --event examples/notifications/github-failure.json
```

The output is the JSON message form that would be sent to Zulip. Preview reads
neither bot credentials nor the network. The examples contain synthetic run links
and commit IDs. Preview them without sending them to the live channel.

To preview the second provider's example, use
`examples/notifications/forgejo-failure.json` instead.
Both producers use the same internal envelope. Each producer fills it from its
trusted CI context; provider webhook parsing and live Forgejo integration remain
separate work.

## Event version 1

See the [GitHub example](../../examples/notifications/github-failure.json) and
[synthetic Forgejo example](../../examples/notifications/forgejo-failure.json).

| Field | Contract |
| --- | --- |
| `schema_version` | Integer `1` |
| `source` | `ci` |
| `provider` | `github` or `forgejo` |
| `event` | `validation_failed` or `validation_recovered` |
| `repository` | Repository name, up to 120 characters |
| `workflow` | Workflow name, up to 120 characters |
| `revision` | Full lowercase Git commit ID: 40 or 64 hexadecimal characters |
| `severity` | Failure: `warning` or `error`; recovery: `info` |
| `idempotency_key` | Stable event identifier, up to 200 characters |
| `evidence_url` | Canonical HTTPS run link, up to 2048 characters; no credentials, query or fragment |
| `destination.channel` | Intended channel, up to 80 characters |
| `destination.topic` | Stable workflow topic, up to 60 characters |
| `recovery_of` | Required for recovery; identifies the earlier failure |

Text fields are single lines with no leading or trailing whitespace. Missing,
unknown, duplicate or incorrectly typed fields are rejected. The file must be
UTF-8 JSON and at most 16 KiB.

The sender requires a failure reference for recovery events. The producer is
responsible for confirming that the earlier failure exists. A successful run
alone is insufficient evidence of recovery.

## Configure a real send

Create a **Generic** bot in the collaboration organization and download its
`zuliprc` file. Store the file outside the repository. On Linux, make it readable
only by its owner:

```sh
chmod 600 /absolute/private/path/zuliprc
```

The command reads `[api]` values `site`, `email` and `key` from that file.
It keeps authentication in an HTTP header and verifies TLS. It uses Python's
default trusted certificates; custom CA/client certificate options from the
official Python bindings are outside this command's current interface.

For a real event, use the following command after substituting the private path,
intended collaboration URL and event path:

```sh
.venv/bin/python scripts/notifications/notify_zulip.py \
  --event /absolute/path/to/real-ci-event.json \
  --send \
  --config /absolute/private/path/zuliprc \
  --site https://collaboration.example.invalid \
  --channel development-events
```

`--site` must match the configuration's organization origin. `--channel` must
match the event's destination. These independent checks catch an accidentally
selected personal-organization configuration or unexpected channel before a
request is sent. The organization URL stays in local configuration and invocation
arguments, outside the event fixtures. Redirects are refused.

On success, the command prints only the confirmed message ID. Input and delivery
errors use controlled diagnostics without printing credentials or server bodies.

## Delivery behavior

- Each request has a ten-second timeout.
- An HTTP 429 rejection can be retried, up to three total attempts. Numeric
  `Retry-After` headers or Zulip's JSON `retry-after` value are honored within a
  ten-second wait budget per retry. Missing delays use one- then two-second waits.
- Longer or unsupported delays produce an error so the operator can try later.
- Authentication errors, redirects, timeouts, server errors and malformed
  acknowledgements end the command without automatic resending.

A connection error or missing acknowledgement can happen after a message was
accepted. Inspect the channel for the event ID before manually retrying.
The `idempotency_key` is included for correlation. It does not provide persistent
deduplication or an exactly-once delivery guarantee. Duplicate/replay handling
remains follow-up work in [#115](https://github.com/ctalaveraw/openops-platform/issues/115).

| Exit | Meaning |
| --- | --- |
| `0` | Preview succeeded, or Zulip confirmed the message ID |
| `1` | Delivery failed or remains unconfirmed |
| `2` | Invalid event, configuration or command arguments |

When integrating the workflow, preserve the validation job's actual result and
report notification failures as warnings. Keep bot credentials in the trusted
notification execution context. Privileged notification code must come from
reviewed source; PR-controlled code and event data must not gain those credentials.
This change makes no workflow or credential-storage changes in GitHub.

## Run offline tests

```sh
.venv/bin/python -m unittest discover -s tests -v
```

The suite uses fake credentials and in-memory HTTP responses. It covers event
validation, provider fixtures, recovery references, message formatting,
organization/channel checks, authentication failures, rate limits, redirects,
timeouts and malformed responses. CLI tests also check exit codes, preview's
credential/network isolation and invocation from another working directory.

`.github/workflows/notifications-tests.yml` runs this same command for changes to
the notification tools and their inputs. It uses the existing pinned checkout
and uv setup actions, read-only repository access, and no Zulip credentials.
The repository-check workflow is unchanged by this feature.

## References

- [Event format task #112](https://github.com/ctalaveraw/openops-platform/issues/112)
- [Notification policy #69](https://github.com/ctalaveraw/openops-platform/issues/69)
- [ChatOps design notes](https://github.com/ctalaveraw/openops-platform-handbook/blob/master/docs/ChatOps-and-AI.md)
- [Zulip send-message API](https://zulip.com/api/send-message)
- [Zulip API keys and configuration files](https://zulip.com/api/api-keys)
