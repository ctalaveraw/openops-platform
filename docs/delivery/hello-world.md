# Hello World delivery

The application is a static banner under `apps/hello-world/public/`.
The other files in that directory are offline validation specimens.
The container includes only the served files.
The NGINX base is pinned to the image digest verified in the PR smoke run;
update that digest through a reviewed change, not a moving base tag.

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
Run the local check without a Docker daemon; run the image check only when
a container engine is available.

## GitHub workflow

`.github/workflows/hello-image.yml` runs the image check on pull requests.
It does not send credentials or publish images from PRs.

For a trusted push to `main` that changes the workload or its delivery
configuration, a separate job builds and checks one image, then publishes that
**same local image** to `ghcr.io/ctalaveraw/openops-platform-hello-world`.
Only that job requests `packages: write`. The tag is `sha-<full Git SHA>`.
The job prints the registry digest; use the digest to identify a release,
not a mutable tag. The registry's package permissions and visibility still
need an operator review. The image is not automatically made public.

GitHub Actions uses a pinned checkout action; its Docker commands and app
checks work outside GitHub. Forgejo runner parity has not been verified.

## Runtime deployment

A successful container smoke test is a temporary deployment on the CI runner.
Publication is not a Kubernetes release. No cluster credentials, Flux files,
production hostnames or live-site changes are included in this PR.

After reviewing the published digest, a separate GitOps change can reference
`ghcr.io/ctalaveraw/openops-platform-hello-world@sha256:<digest>`.
That change needs a named target cluster, ingress, readiness check, and
rollback instructions. Do not use a tag such as `latest` for that step.

## Troubleshooting

- If an offline test fails, run `make -C apps/hello-world test`.
- If Docker is unavailable, the image check exits without publication.
- If HTTP checks fail, the container script prints its logs and removes it.
- If GHCR rejects a push, check repository package permissions; no cluster
  deployment will have occurred.
- To undo a bad deployment later, revert the GitOps digest to a previously
  tested image. Do not delete the old image as a rollback procedure.

The app's [file map](../../apps/hello-world/docs/FILES.md) explains the
individual fixtures; its [Make contract](../../apps/hello-world/docs/MAKE-CONTRACT.md)
explains child ownership. This file covers only delivery wiring.
