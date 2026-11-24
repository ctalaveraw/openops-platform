"""Protect mandatory repository documentation coverage."""

import unittest
from pathlib import Path

from scripts.ci import check_prose


ROOT = Path(__file__).resolve().parents[2]

REQUIRED = {
    "README.md",
    "docs/adr/0001-offline-components.md",
    "contracts/component-v1.md",
    "docs/delivery/hello-world.md",
}


class RequiredProsePolicyTests(unittest.TestCase):
    def test_manifest_retains_mandatory_documents(self) -> None:
        selected = {
            path.relative_to(ROOT).as_posix()
            for path in check_prose.required_markdown_inputs(ROOT)
        }

        self.assertTrue(
            REQUIRED <= selected,
            f"Missing mandatory documents: {sorted(REQUIRED - selected)}",
        )
