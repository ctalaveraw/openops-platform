# Checks

Run these commands from `configuration/`. They use the root Python environment
by default. The coordinator must approve Ansible Core and its dependencies
before adding them to the root lockfile. Ruff and yamllint are existing tools.
Jinja2 and PyYAML are used by the template tests.

| Command | Expected result |
| --- | --- |
| `make lint` | YAML and Python source pass |
| `make syntax` | Ansible parses the playbook and role |
| `make test` | Six tests pass |
| `make prose-check` | Each of the three documents scores 5/5 |
| `make check` | All of the above pass |

If a tool is missing, the target fails. Use `PYTHON` and `ANSIBLE_PLAYBOOK`
to select an approved environment. No target installs tools or runs a play.
Template tests use Jinja2 with strict undefined variables, not the Ansible
runtime. The missing-name test expects an error. Change the fixture inventory
to add a remote host and `make test` should fail. Restore it afterward.

Syntax and template checks cannot prove file permissions or idempotence.
A later test must run in a disposable sandbox as an unprivileged user, with a
fresh private directory matching `/tmp/openops-baseline-*` inside that sandbox.
Check the resulting content and mode, then run the same play again and require
zero changes. Do not use the ARM inventory. Clean-host bootstrap and the
second convergence remain open under #88.
