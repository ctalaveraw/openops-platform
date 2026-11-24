# Infrastructure

The inventory module returns host metadata from two inputs. It uses no providers
and creates no resources. The tests use invented host names.

## Quick start

Install [OpenTofu 1.13.9][release] (MPL-2.0). Verify the download using the
[upstream instructions][install]. GNU Make and Python 3 are also required.

[release]: https://github.com/opentofu/opentofu/releases/tag/v1.13.9
[install]: https://opentofu.org/docs/intro/install/standalone/

From the repository root:

```sh
make -C infrastructure init
make -C infrastructure check
```

Initialization is separate from checks. The module has no remote dependencies,
so initialization also works without network access once the CLI is installed.
The root Makefile does not call this component yet.

## Boundaries

This is a prototype for #18. It does not satisfy the environment map in #86.
The ARM reference environment retains its existing owners. Ansible configures
hosts and Flux manages workloads there. No host or network is managed here.

The [file map](docs/FILES.md) describes the candidate output for configuration
management. See [checks](docs/CHECKS.md) for failure handling.
