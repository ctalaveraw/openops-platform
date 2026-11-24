"""Check the optional component declaration and its existing Make targets."""

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]


class ComponentContractTests(unittest.TestCase):
    def load_contract(self) -> dict:
        content = (ROOT / "contracts/component.json").read_text(encoding="utf-8")
        return json.loads(content)

    def test_manifest_names_the_existing_workload(self) -> None:
        contract = self.load_contract()
        workload = (ROOT / "contracts/workload.yaml").read_text(encoding="utf-8")
        self.assertEqual(contract["schemaVersion"], 1)
        self.assertEqual(contract["name"], "hello-world")
        self.assertEqual(contract["kind"], "fixture")
        self.assertIn("name: hello-world", workload.splitlines())
        self.assertEqual(contract["versionFile"], "VERSION")
        self.assertTrue((ROOT / contract["versionFile"]).is_file())

    def test_runtime_metadata_matches_existing_files(self) -> None:
        runtime = self.load_contract()["runtime"]
        workload = (ROOT / "contracts/workload.yaml").read_text(encoding="utf-8")
        self.assertEqual(runtime["directory"], "public")
        self.assertEqual(runtime["port"], 8080)
        self.assertIn(f"containerPort: {runtime['port']}", workload)
        self.assertIn(f"healthPath: {runtime['healthPath']}", workload)
        self.assertTrue((ROOT / runtime["directory"] / "healthz").is_file())

    def test_make_targets_exist_from_any_working_directory(self) -> None:
        targets = self.load_contract()["makeTargets"]
        self.assertEqual(set(targets), {"help", "check", "lint", "test"})
        for name, target in targets.items():
            with self.subTest(target=name):
                result = subprocess.run(
                    ["make", "--no-print-directory", "-n", "-C", str(ROOT), target],
                    cwd=REPOSITORY,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_parent_can_preview_child_check_without_running_it(self) -> None:
        result = subprocess.run(
            ["make", "--no-print-directory", "-n", "-C", "apps/hello-world", "check"],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("unittest", result.stdout)
        self.assertIn("scripts/verify.py", result.stdout)
        self.assertNotIn("docker build", result.stdout)
        self.assertNotIn("docker compose", result.stdout)
        self.assertNotIn("curl ", result.stdout)

    def assert_public_checksums(self, root: Path) -> None:
        lines = (root / "fixtures/public.sha256").read_text(encoding="utf-8")
        expected = {
            f"public/{p.name}" for p in (root / "public").iterdir() if p.is_file()
        }
        found = set()
        for line in lines.splitlines():
            digest, path = line.split("  ", 1)
            self.assertRegex(digest, r"^[a-f0-9]{64}$")
            self.assertTrue(path.startswith("public/"))
            self.assertNotIn(path, found)
            found.add(path)
            actual = hashlib.sha256((root / path).read_bytes()).hexdigest()
            self.assertEqual(actual, digest)
        self.assertEqual(found, expected)

    def test_source_checksum_manifest_covers_only_public_files(self) -> None:
        self.assert_public_checksums(ROOT)

    def test_mutated_content_does_not_match_committed_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "public", root / "public")
            (root / "fixtures").mkdir()
            shutil.copyfile(
                ROOT / "fixtures/public.sha256", root / "fixtures/public.sha256"
            )
            (root / "public/healthz").write_text("broken\n", encoding="utf-8")
            with self.assertRaises(AssertionError):
                self.assert_public_checksums(root)


if __name__ == "__main__":
    unittest.main()
