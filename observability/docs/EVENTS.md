# Alert event proposal

The JSON fixtures resemble Alertmanager v4 webhooks. They have one alert each.
The fingerprint and URLs are invented. No receiver or mapper is implemented.

Lane 09 should review a CloudEvents 1.0 mapping. Suggested source:
`urn:openops:fixture:alertmanager`. Use each alert's status rather than the
group status when a group contains mixed states.

| Source field | Proposed meaning |
| --- | --- |
| Alert fingerprint and startsAt, scoped by source | Incident occurrence key |
| Occurrence key and transition | Stable event identity for retries |
| Alert status | Type: `dev.openops.alert.firing.v1` or `dev.openops.alert.resolved.v1` |
| Alert labels | Service, severity and owner |
| Alert annotations | Summary and runbook |
| Generator URL | Monitoring evidence link |

Use startsAt and endsAt for the occurrence times. Repeated firing delivery
must not open another incident. A resolved event shares the occurrence key
but has a distinct event ID. A later outage with the same fingerprint has a
new start time. Do not copy the CI-only notification schema.

Lane 08 should review routing to a stable incident topic and how native
Alertmanager delivery interacts with normalized delivery. Choose one
notification path per destination to avoid duplicates. Zulip is optional.
A fabric outage requires an independent route outside the broker.

This proposal does not change the shared event contract or claim delivery.
