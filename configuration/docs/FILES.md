# Files

| Path | Purpose |
| --- | --- |
| `ansible/ansible.cfg` | Local role and inventory lookup |
| `ansible/inventory/fixture.yml` | One local test target |
| `ansible/playbooks/baseline.yml` | Select the fixture role |
| `ansible/roles/baseline_fixture/defaults/main.yml` | Name and destination inputs |
| `ansible/roles/baseline_fixture/tasks/main.yml` | Guard the target and write the file |
| `ansible/roles/baseline_fixture/templates/baseline.txt.j2` | File content |
| `tests/test_baseline.py` | Input and render assertions |
| `Makefile` | Local check commands |

The fixture inventory is not the infrastructure output contract from
issue #86. A shared inventory format needs review by lanes 04 and 00.
