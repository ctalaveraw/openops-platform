# Forge adapters

Read-only, offline-testable adapters for the GitHub and Forgejo APIs. The first
operation reads a pull-request summary and maps it to a candidate CloudEvents
1.0 structured JSON record. GitHub remains the canonical OpenOps repository.
This component changes neither forge, nor any pull request.

## Try it locally

```sh
cd integrations/forge
make check
python3 forge_adapter.py --provider github \
  --repository example/openops-platform --number 17 \
  --fixture fixtures/github-pr.json
python3 forge_adapter.py --provider forgejo \
  --repository example/openops-platform --number 31 \
  --site https://forge.example.invalid --fixture fixtures/forgejo-pr.json
```

`--fixture` always reads a local synthetic response. The command never makes
an HTTP request. `fetch_pull_request()` is a separate, read-only library helper.
Tests substitute an in-memory HTTP opener; they never contact either forge.
Neither command nor helper supports credentials in this first revision.

## Candidate interface

`normalize(provider, repository, number, payload, site=...)` returns one
CloudEvents-shaped *snapshot*:

- `source`: provider repository URL
- `id`: deterministic hash of provider, repository, PR number, state and head SHA
- `subject`: `pulls/<number>`
- `type`: `dev.openops.forge.pull_request.snapshot.v1`
- `data`: provider, repository, number, state, revision, logical change ID,
  source URL and candidate schema version

The two synthetic PR responses use the same commit SHA and repository name.
They share `data.logical_change`, but have different `id` and `source` values.
This is not a webhook event and has no timestamp, delivery guarantee or proof
of an actual CI run. An unchanged snapshot produces the same ID when read
again. A different head SHA or merged state produces a different ID.

The schema and event names remain **candidates** until Lane 09 (#146) and
coordination (Lane 00) approve the cross-plane contract. The existing version-1
CI notifier (#112) is not changed. Nothing sends events to Zulip or NATS.

## Limitations

Only PR number, state, merged marker, head SHA and URL are retained. Review
status, required checks, merge conflicts, requested reviewers and independent
CI run IDs are not represented. The helper reads unauthenticated public GET
endpoints only; private repositories require a separately reviewed credential
boundary. GitHub and Forgejo APIs have not been exercised live.

Do not infer cross-forge CI success, native feature parity, or deployment
approval from a matching Git revision.

See the [capability matrix](docs/CAPABILITIES.md), [file inventory](docs/FILES.md)
and [check instructions](docs/CHECKS.md).
