# Infrastructure files

| Path | Purpose |
| --- | --- |
| `Makefile` | Local commands |
| `.gitignore` | Exclude generated state and plan files |
| `terraform/modules/inventory/main.tf` | Inputs and metadata output |
| `terraform/modules/inventory/tests/inventory.tofutest.hcl` | Plan assertions and rejected inputs |
| `docs/CHECKS.md` | Check commands and recovery |

## Candidate inventory output

For the ARM64 test case, the output value is:

```json
{
  "schema_version": 1,
  "hosts": {
    "fixture-node": {
      "architecture": "arm64"
    }
  }
}
```

The host key is a logical label. The architecture uses OCI-style names.
There are no addresses or connection credentials. This is not an Ansible
inventory. Lane 00 and lane 05 must agree on the interface before any consumer
uses it. The configuration lane's localhost fixture remains independent.
