# OpenOps Platform

[![Repository checks](https://github.com/ctalaveraw/openops-platform/actions/workflows/lint.yml/badge.svg?branch=main&event=push)](https://github.com/ctalaveraw/openops-platform/actions/workflows/lint.yml)

OpenOps is a shared platform engineering project. We are building a reference
environment for independently operated developer tooling and reproducible
infrastructure. The planned work covers secure software delivery through GitOps,
with observability and recovery procedures for deployed services.

## Project status

**Source checks and a disposable app are implemented.** The Hello World fixture
can be tested without a container or a cluster. The delivery workflow tests a
local container on PRs and is configured to publish from trusted `main` pushes.
No live Kubernetes deployment has been verified.

## First workload

The [Hello World fixture](apps/hello-world/README.md) is a static test workload.
Run `make check-apps` to validate it independently or `make check` to validate
both the platform and the workload. Neither command builds or deploys an image.

See [Hello World delivery](docs/delivery/hello-world.md) for the image smoke test,
trusted registry publication, and the separate runtime-deployment boundary.

## Engineering handbook

The [OpenOps Platform Engineering Handbook](https://github.com/ctalaveraw/openops-platform-handbook) maintains the project charter, architecture options, decision register, technical evaluations, and proposed roadmap. Planning is intentionally separated from executable infrastructure and application code.

- [Project charter](https://github.com/ctalaveraw/openops-platform-handbook/blob/master/docs/Project-Charter.md)
- [Platform architecture](https://github.com/ctalaveraw/openops-platform-handbook/blob/master/docs/Platform-Architecture.md)
- [Decision register](https://github.com/ctalaveraw/openops-platform-handbook/blob/master/docs/Decision-Register.md)
- [Roadmap and acceptance criteria](https://github.com/ctalaveraw/openops-platform-handbook/blob/master/docs/Roadmap-and-Acceptance.md)

## Engineering approach

- Applications remain independently testable, locally runnable, and loosely coupled to platform services.
- Application images are built and qualified once, then promoted by immutable digest.
- CI, deployment reconciliation, host provisioning, and secrets management have distinct authorities.
- Critical workflows are reproducible using owned scripts, portable tools, and standard interfaces.
- Reviewable changes, failure tests, and recovery evidence are prerequisites for declaring work complete.

The first workload is the static Hello World fixture. GitHub remains the
canonical source repository. Forgejo and Zulip are operated separately in the
homelab; OpenOps-specific rollout and parity checks remain independent tasks.

## Local checks

### Markdown

Use Git, GNU Make, and uv 0.13.9.
Run `make bootstrap`, then `make check`.
Bootstrap installs Python 3.12 in uv's managed storage.
Python tooling and Node/npm live in `.venv`.
JavaScript linters live in ignored `node_modules/`.

See [the Markdown check instructions](docs/ci/markdown.md).

### YAML

Run `make lint-yaml` to check repository YAML.
This check also runs through `make check`.

See [the YAML check instructions](docs/ci/yaml.md).

### Python

Run `make lint-python` to check Python lint and formatting.
This check also runs through `make check`.

See [the Python check instructions](docs/ci/python.md).

### Shell

Run `make lint-shell` to check repository shell scripts.
This target also runs through `make check`.

See [the shell check instructions](docs/ci/shell.md).

### JSON

Run `make lint-json` to parse repository JSON and validate notification examples.
This target also runs through `make check`.

See [the JSON check instructions](docs/ci/json.md).

### TOML

Run `make lint-toml` to parse repository TOML, including `uv.lock`.
This target also runs through `make check`.

See [the TOML check instructions](docs/ci/toml.md).

### Makefiles

Run `make lint-make` to check Makefile source and the public command interface.
This target also runs through `make check`.

See [the Makefile check instructions](docs/ci/make.md).

### HTML and CSS

Run `make lint-web` to check application HTML and CSS.
This target also runs through `make check`.

See [the web check instructions](docs/ci/web.md).

### Prose

Run `make lint-prose` to review English prose in `README.md` and `docs/`.

See [the prose check instructions](docs/ci/prose.md).

### Actions

Run `make validate-actions` to validate GitHub workflow definitions.
This target also runs through `make check`.

See [the Actions validation instructions](docs/ci/actions.md).

### CI

The GitHub Actions workflow runs the required checks for pull requests and pushes to `main`.

See [the workflow instructions and action inventory](docs/ci/checks.md).
