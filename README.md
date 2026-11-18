# OpenOps Platform

A collaborative platform-engineering reference environment focused on independently operated developer tooling, reproducible infrastructure, secure software delivery, GitOps, observability, and operational recovery.

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
