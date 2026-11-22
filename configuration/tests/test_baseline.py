"""Test the fixture inputs and template without invoking a playbook."""

import unittest
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined, UndefinedError

ANSIBLE = Path(__file__).resolve().parents[1] / "ansible"
ROLE = ANSIBLE / "roles/baseline_fixture"


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def render(values):
    source = (ROLE / "templates/baseline.txt.j2").read_text(encoding="utf-8")
    env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
    return env.from_string(source).render(values)


class BaselineTests(unittest.TestCase):
    def test_default_template(self):
        defaults = load_yaml(ROLE / "defaults/main.yml")
        self.assertEqual(render(defaults), "name=openops-fixture\nmanaged_by=ansible\n")

    def test_name_override(self):
        self.assertEqual(
            render({"baseline_fixture_name": "lab"}), "name=lab\nmanaged_by=ansible\n"
        )

    def test_missing_name_is_rejected(self):
        with self.assertRaises(UndefinedError):
            render({})

    def test_inventory_is_local_only(self):
        inventory = load_yaml(ANSIBLE / "inventory/fixture.yml")
        self.assertEqual(
            inventory,
            {
                "all": {
                    "children": {
                        "baseline_fixture": {
                            "hosts": {
                                "localhost": {
                                    "ansible_connection": "local",
                                    "ansible_become": False,
                                }
                            }
                        }
                    }
                }
            },
        )

    def test_play_targets_fixture_only(self):
        (play,) = load_yaml(ANSIBLE / "playbooks/baseline.yml")
        self.assertEqual(play["hosts"], "baseline_fixture")
        self.assertEqual(play["connection"], "local")
        self.assertIs(play["become"], False)
        self.assertIs(play["gather_facts"], False)
        self.assertEqual(play["roles"], ["baseline_fixture"])

    def test_destination_is_unset_by_default(self):
        defaults = load_yaml(ROLE / "defaults/main.yml")
        self.assertEqual(defaults["baseline_fixture_dir"], "")


if __name__ == "__main__":
    unittest.main()
