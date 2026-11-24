# ADR 0001: Offline component boundaries

Status: accepted in PR #218.
Owner: repository maintainers.

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

| Responsibility | Current scope | Destination |
| --- | --- | --- |
| Repository maintainers | Root Make, shared CI, locks, ADRs and contracts | Existing root paths |
| Platform validation | `scripts/ci/`, `docs/ci/`, `tests/validation/` | `platform/` |
| Application workload | `apps/hello-world/` | Unchanged |
| Application delivery | `scripts/delivery/`, `docs/delivery/` | `delivery/` |
| Infrastructure provisioning | New provisioning modules | `infrastructure/` |
| Configuration management | New host configuration | `configuration/` |
| Policy and security | New policy rules | `policy/` |
| Forge integrations | New forge adapters | `integrations/forge/` |
| ChatOps notifications | `scripts/notifications/`, `tests/notifications/`, `examples/notifications/` | `integrations/chatops/` |
| Gotify adapter | Gotify-specific integration | `integrations/chatops/gotify/` |
| Event processing | New event schemas and mappings | `events/` |
| Observability | Monitoring rules and tests | `observability/` |
| Recovery operations | Recovery design | Path to be agreed |
| Cross-component testing | Integration test design | `tests/integration/` after review |
| Reference operations | ARM homelab services | Separate ARM homelab repository |
| Issue and PR tracking | GitHub records | No source directory |

ChatOps owns the shared notification behavior. The Gotify adapter owns its
provider-specific implementation. Changes to shared interfaces require review
by repository maintainers. Dependency proposals must name the version and
license, explain why the tool is needed, and show how to test it. Repository
maintainers own root locks and generic workflow wiring. Separate feature
branches keep unrelated changes out of a PR.

## Admission

Follow [component contract v1](../../contracts/component-v1.md).
A reviewed change adds explicit root delegation after the child passes real
positive and negative checks. Keep repository-wide source lint. Do not call
the parent check from a child. No automatic discovery of executable targets.

## Delivery pause

Keep existing delivery code. Automatic image triggers are disabled while
components are developed offline. Manual validation does not grant publication
rights. Publication requires a separate explicit request on canonical main.
Do not run either operation during the pause without authorization.

See [delivery instructions](../delivery/hello-world.md) and
[repository checks](../ci/checks.md). Re-enable automatic delivery only in a
reviewed change with protection and runtime acceptance reviewed again.

## Consequences

Component tests can run before deployment. A new component is not part of the
root gate until admitted. Live service integration, recovery and forge parity
need their own evidence. Revisit these boundaries if a component cannot be
tested or changed without coupling to another.

Repository documents and correspondence follow the
[engineering writing standard](../engineering-writing.md).
