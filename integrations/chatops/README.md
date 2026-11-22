# ChatOps routing preview

This component checks the existing CI notifier and previews a proposed PR topic
for [#197](https://github.com/ctalaveraw/openops-platform/issues/197).
It uses the version-1 event file accepted by the notifier. Scripts, fixtures and
tests remain in their current directories.

## Quick start

Run `make bootstrap` at the repository root once. Then run:

```sh
make -C integrations/chatops check
make -C integrations/chatops preview
```

To compare the synthetic Forgejo record:

```sh
.venv/bin/python -B scripts/notifications/preview_route.py \
  --event examples/notifications/forgejo-failure.json --pull-request 123
```

The command prints a message form. It has no send option. The caller supplies
the PR number explicitly because the legacy event has no PR field. The event's
channel, content, evidence link and opaque event ID are preserved.

| Provider | Repository | PR | Proposed topic |
| --- | --- | --- | --- |
| GitHub | `example/openops-platform` | 123 | `github example/openops-platform PR #123` |
| Forgejo | `example/openops-platform` | 123 | `forgejo example/openops-platform PR #123` |

A failure and its correlated recovery use the same topic. Repeated previews
produce the same output. Topic names over the existing 60-character limit are
rejected without shortening.

## Review boundaries

The topic format is a proposal. This preview assumes one configured instance per
provider. Lane 07 must confirm repository labels, PR numbers and instance identity
from trusted forge context. Multiple Forgejo instances and aliases for long names
need a reviewed mapping before activation. Topic renames, linkifiers and native
bot topic compatibility remain acceptance work in #197.

Lane 09 proposes conversion from normalized CI events to the existing notifier
file under issue #146. Its caller supplies the destination policy. Keep the event
ID opaque. This preview consumes only that legacy shape. Monitoring and Gotify
events need their own adapters outside the CI parser.

Lane 00 owns shared contracts, root checks and any path migration. This component
adds no dependencies or root delegation. Native GitHub activity remains with the
existing integration. Mirrored activity should not create another announcement.

The sender does not persist receipts. Submitting the same event twice can post
twice. Delivery/replay acceptance remains in #115. Trusted CI wiring stays in #65.
Bot permissions require server-side tests in #199. Notification preferences
are tracked in #201. Interactive lookups are separate work in #205.

See the [check commands](docs/CHECKS.md) and [file map](docs/FILES.md).
The [notifier guide](../../docs/ci/zulip-notifications.md) documents the v1 contract.
