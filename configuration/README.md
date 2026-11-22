# Configuration management

This Ansible fixture manages one text file. It uses a local inventory rather
than the ARM lab hosts. No service, package or account is managed here.

## Quick start

From the repository root, run `make -C configuration help`.
Run `make -C configuration check` after the required tools are installed.
See [checks](docs/CHECKS.md) for the tool requirements and failure cases.

The playbook is for syntax checks at present. File convergence requires a
separate sandbox test. Do not run it against a workstation or lab inventory.
The destination is unset by default.

See [files](docs/FILES.md) for the role layout.
