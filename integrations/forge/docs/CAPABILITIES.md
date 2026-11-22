# GitHub and Forgejo capability inventory

Checked against the project issues and source on 2026-11-22. Entries marked
"candidate" are not evidence that a live Forgejo endpoint has passed a test.
GitHub remains canonical; the private Forgejo environment is a reference target.

| Capability | Category | Evidence and next check |
| --- | --- | --- |
| Git source, commits and tags | Native Git | Existing ARM repository mirroring proves its own Git paths. OpenOps mirror parity remains #108. |
| PR listing and detail lookup | Native API with adapter for common output | This component has synthetic GitHub/Forgejo PR fixtures and mocked GET responses. Live parity unverified. |
| CI runner execution | Native on each provider; shared scripts | #106 requires the OpenOps checks under Forgejo, not merely the ARM repo's CI results. |
| Commit statuses and PR checks | Adapter | #183 proposes provider-specific reporting. No write API is implemented here. |
| Protected branches, token and runner permissions | Native controls, adapter for read-only comparison | #110 and #185; unsupported API reads must report unknown, not success. |
| Release notes | Portable CLI | #178 uses source history and needs no provider API for generation. |
| Publishing forge Releases | Adapter | #179. No release creation in this component. |
| OCI registry copy and digest verification | Portable OCI tooling | #180. This component does not publish images. |
| Promotion pull requests | Provider write adapter, deferred | #189. A PR write is outside this first read-only implementation. |
| CI duration and failure comparison | Adapter to provider result APIs | #190. Two runs of the same revision remain separate results. |
| Issues, labels, and project boards | Native features, metadata portability unverified | #184 and #186. No issue changes or bidirectional sync. |
| Code scanning user interface | Different provider capabilities | #169. Portable scanner evidence is required even without an equivalent dashboard. |
| Zulip notifications | Native when sufficient; separate ChatOps adapter | #68/#107 and Lane 08 own delivery. This adapter never sends chat messages. |
| Shared CloudEvents event format | Contract owned by Lane 09 | #146; this PR contains only a candidate snapshot, no shared schema modification. |

The current API snapshot is read-only. A shared Git revision is a correlation
hint, not proof of CI equality, PR identity or release status. Its `id` changes
when provider, PR state or head SHA changes; `data.logical_change` may match
across providers. No durable deduplication or webhook-signature verification
is implied.

## Duplicate issues reconciled

Closed #187 repeated release planning already tracked in #178/#179. Closed
#188 repeated OCI digest replication already tracked in #180. Their closure
comments explicitly state that no implementation was completed. Neither is
used as evidence of forge parity.

## Questions for coordination and events

- Lane 00: accept PR snapshot as a temporary local adapter output under #111,
  without integrating it into the root workflow or making it authoritative?
- Lane 09 (#146): approve or change the candidate CloudEvents type, `id`,
  `source`, `subject`, `data.logical_change` and schema-version placement. A
  snapshot is not an occurrence event; should the event fabric accept it as
  telemetry or only convert actual webhook/CI occurrences?
- Lane 90: decide where to test correlation of snapshots with actual CI run
  events after the interfaces are approved. Do not combine provider results
  solely because they refer to the same source SHA.
