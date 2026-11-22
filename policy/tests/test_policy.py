"""Use the real policy evaluator on safe, unsafe and malformed input."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "scripts/evaluate.py"
FIXTURES = ROOT / "fixtures"


class DeploymentPolicyTests(unittest.TestCase):
    def evaluate(self, *paths):
        process = subprocess.run(
            [sys.executable, str(EVALUATOR), "--format", "json", *map(str, paths)],
            cwd=ROOT.parent,
            capture_output=True,
            text=True,
            check=False,
        )
        return process, json.loads(process.stdout)

    def test_pinned_safe_deployment_allowed(self):
        process, reports = self.evaluate(FIXTURES / "allowed/safe.json")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(reports[0]["status"], "allow")
        self.assertEqual(reports[0]["findings"], [])
        self.assertEqual(reports[0]["version"], "openops-policy-report/v1")

    def test_mutable_image_denied(self):
        process, reports = self.evaluate(FIXTURES / "denied/mutable-tag.json")
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertEqual(reports[0]["status"], "deny")
        self.assertEqual(
            {finding["id"] for finding in reports[0]["findings"]},
            {"K8S-IMAGE-001"},
        )

    def test_privilege_denied(self):
        process, reports = self.evaluate(FIXTURES / "denied/privileged.json")
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertEqual(reports[0]["status"], "deny")
        self.assertEqual(
            {finding["id"] for finding in reports[0]["findings"]},
            {"K8S-PRIV-001"},
        )

    def test_required_health_and_metadata_denied(self):
        process, reports = self.evaluate(
            FIXTURES / "denied/missing-health-and-labels.json"
        )
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertEqual(reports[0]["status"], "deny")
        self.assertEqual(
            {finding["id"] for finding in reports[0]["findings"]},
            {"K8S-METADATA-001", "K8S-HEALTH-001"},
        )

    def test_malformed_json_is_error_not_denial(self):
        process, reports = self.evaluate(FIXTURES / "invalid/broken.json.txt")
        self.assertEqual(process.returncode, 2)
        self.assertEqual(reports[0]["status"], "error")
        self.assertEqual(reports[0]["error"]["category"], "parse")
        self.assertEqual(reports[0]["findings"], [])

    def test_unsupported_kind_is_error_not_allow(self):
        process, reports = self.evaluate(
            FIXTURES / "invalid/unsupported-kind.json"
        )
        self.assertEqual(process.returncode, 2)
        self.assertEqual(reports[0]["status"], "error")
        self.assertEqual(reports[0]["error"]["category"], "unsupported")

    def test_invalid_structure_is_error_not_denial(self):
        process, reports = self.evaluate(
            FIXTURES / "invalid/malformed-structure.json"
        )
        self.assertEqual(process.returncode, 2)
        self.assertEqual(reports[0]["status"], "error")
        self.assertEqual(reports[0]["error"]["category"], "structure")

    def test_mixed_results_return_parse_error(self):
        process, reports = self.evaluate(
            FIXTURES / "denied/mutable-tag.json",
            FIXTURES / "invalid/broken.json.txt",
        )
        self.assertEqual(process.returncode, 2)
        self.assertEqual([r["status"] for r in reports], ["deny", "error"])

    def test_missing_file_never_passes(self):
        process, reports = self.evaluate(FIXTURES / "missing.json")
        self.assertEqual(process.returncode, 2)
        self.assertEqual(reports[0]["status"], "error")

    def test_check_does_not_modify_specimens(self):
        path = FIXTURES / "allowed/safe.json"
        original = hashlib.sha256(path.read_bytes()).hexdigest()
        self.evaluate(path)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), original)

    def test_validation_does_not_create_files(self):
        path = FIXTURES / "allowed/safe.json"
        with tempfile.TemporaryDirectory() as scratch:
            before = list(Path(scratch).iterdir())
            process = subprocess.run(
                [sys.executable, str(EVALUATOR), str(path)],
                cwd=scratch,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(list(Path(scratch).iterdir()), before)


if __name__ == "__main__":
    unittest.main()
