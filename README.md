# OpenOps Platform

OpenOps is a shared platform engineering project. We are building a reference
environment for independently operated developer tooling and reproducible
infrastructure. The planned work covers secure software delivery through GitOps,
with observability and recovery procedures for deployed services.

## Project status

**Foundation and architecture planning.** The intended system is documented but must not be assumed to be deployed. Work proceeds in independently testable milestones; implementation and operational claims require evidence from this repository.

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

The initial candidate workload is a browser-rendered static application. A Forgejo-first control plane and team communication system are planned for evaluation. Neither choice should be described as implemented until verified.

## Local checks

### Markdown

Use Git, GNU Make, and uv 0.13.9.
Run `make bootstrap`, then `make check`.
Bootstrap installs Python 3.12 in uv's managed storage and the locked tools in `.venv`.

See [the Markdown check instructions](docs/ci/markdown.md).

### Prose

Run `make lint-prose` to review English prose in `README.md` and `docs/`.

See [the prose check instructions](docs/ci/prose.md).
