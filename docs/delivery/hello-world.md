# Hello World delivery

The application is a static banner under `apps/hello-world/public/`.
The other files in that directory are offline validation specimens.
The container includes only the served files.
The NGINX base is pinned to the image digest verified in the PR smoke run.
Update that digest through a reviewed change, not a moving base tag.

## Independent and combined checks

| Command | Runs | Needs Docker? |
| --- | --- | --- |
| `make -C apps/hello-world check` | App-owned tests | No |
| `make check-apps` | The same child tests, called by the root Makefile | No |
| `make check` | Platform lint, workflow validation and child tests | No |
| `sh scripts/delivery/check_hello_image.sh` | Build, non-root check and HTTP smoke | Yes |
| `make -C apps/hello-world up` | Optional local Compose server | Yes |

The root Makefile does not import application Python. The image-check script
calls the app's `build`, `compose-check` and `smoke` targets.
Run the local check without a Docker daemon. Run the image check only when
a container engine is available.

## GitHub workflow

The image workflow is manual. Pull requests and pushes run the existing
repository checks, not the image workflow. The prior delivery implementation
and evidence from PR #164 remain in Git.

After review and explicit authorization, select Actions, Hello World image,
Run workflow. Choose a branch and an operation:

| Operation | Allowed source | Effect |
| --- | --- | --- |
| `validate` (default) | Selected ref | Build and smoke-test locally on a runner. No registry write. |
| `publish` | Canonical `main` only | Build, test and push the same image to GHCR. |

Both operations are deferred during offline development. An unauthorized
publish request fails without running a build. The publish job alone requests
`packages: write`. The dispatch requires repository write access. This job
guard does not replace repository permissions or an independently enforced
deployment approval. Do not rerun historical push-based image runs.

Publication tags the image with `sha-<full Git SHA>` and records the digest.
Registry visibility and permissions still need review. Forgejo parity remains
untested. The scripts can run outside GitHub.

## Runtime deployment

A successful container smoke test is a temporary deployment on the CI runner.
Publication is not a Kubernetes release. No cluster credentials, Flux files,
production hostnames or live-site changes are part of this workflow.

After reviewing the published digest, a separate GitOps change can reference
`ghcr.io/ctalaveraw/openops-platform-hello-world@sha256:<digest>`.
That change needs a named target cluster, ingress, readiness check, and
rollback instructions. Do not use a tag such as `latest` for that step.

## Troubleshooting

- If an offline test fails, run `make -C apps/hello-world test`.
- If Docker is unavailable, the image check exits without publication.
- If HTTP checks fail, the container script prints its logs and removes it.
- If GHCR rejects a push, check repository package permissions. No cluster
  deployment will have occurred.
- To undo a bad deployment later, revert the GitOps digest to a previously
  tested image. Do not delete the old image as a rollback procedure.

The app's [file map](../../apps/hello-world/docs/FILES.md) explains the
individual fixtures. Its [Make contract](../../apps/hello-world/docs/MAKE-CONTRACT.md)
explains child ownership. This file covers only delivery wiring.
