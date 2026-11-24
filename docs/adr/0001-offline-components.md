# ADR 0001: Offline component boundaries

Status: proposed for review. Merge records acceptance.
Owner: lane 00. Reviewers: project maintainers.

## Decision

The platform is the deliverable. Hello World stays a disposable static site.
Each component owns its checks. Root Make delegates to admitted components.
Keep the current repository instead of splitting each component into a repo.
This avoids duplicating tooling and makes interfaces reviewable in one PR.

GitHub is canonical. Forgejo is a portability target. The handbook holds
long-form design and learning material. The ARM homelab repository owns actual
service installations and environment configuration.

## Directory ownership

Paths in the destination column need not exist yet. Existing paths stay until
a dedicated migration PR. Tests stay with their component.

| Lane | Current scope | Destination |
| --- | --- | --- |
| 00 | Root Make, shared CI, locks, ADRs and contracts | Same |
| 01 | `scripts/ci/`, `docs/ci/`, `tests/validation/` | `platform/` |
| 02 | `apps/hello-world/` | Same |
| 03 | `scripts/delivery/`, `docs/delivery/` | `delivery/` |
| 04 | New provisioning modules | `infrastructure/` |
| 05 | New host configuration | `configuration/` |
| 06 | New policy rules | `policy/` |
| 07 | New forge adapters | `integrations/forge/` |
| 08 | `scripts/notifications/`, `tests/notifications/`, `examples/notifications/` | `integrations/chatops/` |
| 08G | Gotify adapter only | `integrations/chatops/gotify/` |
| 09 | New event schemas and mappings | `events/` |
| 10 | Monitoring rules and tests | `observability/` |
| 11 | Recovery design | Path to be agreed |
| 90 | Cross-component test design | `tests/integration/` after review |
| 91, 92 | Reference environment | ARM homelab repository |
| 99 | Issue and PR tracking | No source ownership |

Lane 08 excludes the Gotify subdirectory. Shared interface changes from any
lane go through 00. A component can propose a dependency by naming its version and license.
Explain why it is needed and how to install and test it. Only 00 edits root locks and generic
workflow wiring. Separate feature branches keep unrelated changes out of a PR.

## Admission

Follow [component contract v1](../../contracts/component-v1.md).
A reviewed change adds explicit root delegation after the child passes real
positive and negative checks. Keep repository-wide source lint. Do not call
the parent check from a child. No automatic discovery of executable targets.

## Delivery pause

Keep existing delivery code. Remove automatic image triggers while the team
builds components offline. Manual validation does not grant publication rights.
Publication requires a separate explicit request on canonical main.
Do not run either operation during the pause without authorization.

See [delivery instructions](../delivery/hello-world.md) and
[repository checks](../ci/checks.md). Re-enable automatic delivery only in a
reviewed change with protection and runtime acceptance reviewed again.

## Consequences

Component tests can run before deployment. A new component is not part of the
root gate until admitted. Live service integration, recovery and forge parity
need their own evidence. Revisit these boundaries if a component cannot be
tested or changed without coupling to another.
