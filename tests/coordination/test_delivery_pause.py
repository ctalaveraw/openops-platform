"""Protect the offline delivery boundary without starting a workflow."""

import copy
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github/workflows"

PUBLISH_GUARD = (
    "github.event_name == 'workflow_dispatch' && "
    "inputs.operation == 'publish' && "
    "github.ref == 'refs/heads/main' && "
    "github.repository == 'ctalaveraw/openops-platform'"
)
VERIFY_GUARD = (
    "github.event_name == 'workflow_dispatch' && inputs.operation == 'validate'"
)
REJECT_GUARD = (
    "github.event_name == 'workflow_dispatch' && "
    "inputs.operation == 'publish' && "
    "(github.ref != 'refs/heads/main' || "
    "github.repository != 'ctalaveraw/openops-platform')"
)


class DeliveryPauseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = yaml.safe_load(
            (WORKFLOWS / "hello-image.yml").read_text(encoding="utf-8")
        )

    def assert_manual_only(self, workflow: dict) -> None:
        self.assertEqual(set(workflow["on"]), {"workflow_dispatch"})
        inputs = workflow["on"]["workflow_dispatch"]["inputs"]["operation"]
        self.assertEqual(inputs["type"], "choice")
        self.assertTrue(inputs["required"])
        self.assertEqual(inputs["default"], "validate")
        self.assertEqual(inputs["options"], ["validate", "publish"])
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        jobs = workflow["jobs"]
        self.assertEqual(set(jobs), {"reject", "verify", "publish"})
        self.assertEqual(jobs["verify"]["if"], VERIFY_GUARD)
        self.assertEqual(jobs["reject"]["if"], REJECT_GUARD)
        self.assertEqual(jobs["publish"]["if"], PUBLISH_GUARD)
        for name in ("reject", "verify"):
            self.assertEqual(
                jobs[name].get("permissions", workflow["permissions"]),
                {"contents": "read"},
            )
        self.assertEqual(
            jobs["publish"]["permissions"],
            {"contents": "read", "packages": "write"},
        )

    def test_manual_delivery_contract(self) -> None:
        self.assert_manual_only(self.workflow)

    def test_automatic_triggers_are_rejected(self) -> None:
        for event in ("push", "pull_request", "schedule", "workflow_call"):
            with self.subTest(event=event):
                changed = copy.deepcopy(self.workflow)
                changed["on"][event] = {}
                with self.assertRaises(AssertionError):
                    self.assert_manual_only(changed)

    def test_publish_default_is_rejected(self) -> None:
        changed = copy.deepcopy(self.workflow)
        changed["on"]["workflow_dispatch"]["inputs"]["operation"]["default"] = "publish"
        with self.assertRaises(AssertionError):
            self.assert_manual_only(changed)

    def test_weakened_publish_guard_is_rejected(self) -> None:
        for guard in (
            "inputs.operation == 'publish'",
            PUBLISH_GUARD.split(" && github.repository")[0],
            PUBLISH_GUARD.replace("refs/heads/main", "refs/heads/other"),
        ):
            with self.subTest(guard=guard):
                changed = copy.deepcopy(self.workflow)
                changed["jobs"]["publish"]["if"] = guard
                with self.assertRaises(AssertionError):
                    self.assert_manual_only(changed)

    def test_validation_write_access_is_rejected(self) -> None:
        changed = copy.deepcopy(self.workflow)
        changed["jobs"]["verify"]["permissions"] = {"packages": "write"}
        with self.assertRaises(AssertionError):
            self.assert_manual_only(changed)

    def test_repository_checks_remain_automatic(self) -> None:
        workflow = yaml.safe_load((WORKFLOWS / "lint.yml").read_text(encoding="utf-8"))
        self.assertEqual(set(workflow["on"]), {"pull_request", "push"})
        self.assertEqual(workflow["on"]["push"]["branches"], ["main"])
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        self.assertEqual(workflow["jobs"]["checks"]["steps"][-1]["run"], "make check")


if __name__ == "__main__":
    unittest.main()
