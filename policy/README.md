# Policy exercises

This component checks sample Kubernetes Deployment JSON without a cluster.
It is a source-level exercise for OpenOps issue #172, not an admission policy.
No root CI workflow invokes this component yet.

Run from this directory:

```sh
make help
make check
python3 scripts/evaluate.py fixtures/allowed/safe.json
python3 scripts/evaluate.py fixtures/denied/mutable-tag.json
```

The last command deliberately exits 1. Deployment JSON is valid Kubernetes
input. The checker does not parse Kubernetes YAML or rendered Helm output.

## Scope

The first exercise covers one-container `apps/v1` Deployments. It requires a
SHA-256 image reference, a non-root unprivileged container, HTTP health probes,
and a matching application-name label. Unsupported kinds produce an error,
not a passing result. The checker does not verify a digest exists in a registry.

No policy decision affects a PR, a registry, or a running cluster.
Refer to [file map](docs/FILES.md), [checks](docs/CHECKS.md) and
[policy decisions](docs/POLICY.md) before extending this component.
