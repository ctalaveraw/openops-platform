# Deployment policy v1

## Engine decision

The first rules use Python's standard library. They run without package
installation, cluster access or a language-specific policy runtime. Rule IDs
and the JSON report stay separate from evaluation code.

Conftest 0.71.1 with OPA/Rego v1 is the candidate for a later migration.
Conftest is Apache-2.0 licensed. It can test JSON and YAML files without a
cluster, but is not part of the current root tool lock. Its binary was not
available for local verification. Lane 00 must review a pinned bootstrap path
before using it for required checks. We have not claimed Rego parity.

## Rules

| ID | Requirement |
| --- | --- |
| `K8S-IMAGE-001` | Image uses `@sha256:` followed by 64 lowercase hex characters |
| `K8S-PRIV-001` | Privileged is not true, runAsNonRoot is true |
| `K8S-METADATA-001` | Deployment and pod labels match the Deployment name |
| `K8S-HEALTH-001` | Readiness and liveness HTTP probes include path and port |
| `K8S-SCOPE-001` | Only one container is supported by this exercise |

The checker accepts only an `apps/v1` Deployment object. Input structure
errors are separate from policy denials. This is not a complete Kubernetes
schema validator. It does not support YAML, init containers, sidecars,
CronJobs or custom resources. It does not validate registry access.

## Exceptions

No exceptions are active or automatically applied. A proposed exception must
name a human owner, one rule ID, the affected file or workload, a reason,
a tracking issue and an expiration date in UTC. The owner proposes it in a PR.
A separate reviewer approves it. The validity period must be finite, and an
expired exception cannot be renewed without review. The policy stays denying
until an exception mechanism and its expiry tests are implemented and approved.

Scanner vulnerability severity thresholds belong to issue #62, not this
static Deployment rule exercise. Live admission is a separate reviewed change.
