"""Test selection of required repository prose documents."""

import tempfile
import unittest
from pathlib import Path

from scripts.ci import check_prose


REQUIRED = (
    "README.md",
    "docs/adr/0001-offline-components.md",
    "contracts/component-v1.md",
    "docs/delivery/hello-world.md",
)


class RequiredProseTests(unittest.TestCase):
    def create_documents(self, root: Path) -> None:
        for name in REQUIRED:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Test documentation.\n", encoding="utf-8")

            manifest = root / "scripts/ci/required-prose.txt"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(
                "\n".join(REQUIRED) + "\n",
                encoding="utf-8",
            )

    def test_selects_all_required_documents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_documents(root)

            paths = check_prose.required_markdown_inputs(root)

            self.assertEqual(
                [path.relative_to(root).as_posix() for path in paths],
                list(REQUIRED),
            )

    def test_missing_required_document_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_documents(root)
            (root / "contracts/component-v1.md").unlink()

            with self.assertRaisesRegex(ValueError, r"contracts/component-v1\.md"):
                check_prose.required_markdown_inputs(root)

                def required_markdown_inputs(root: Path) -> list[Path]:
                    """Select required prose documents from the checked-in manifest."""
                    manifest = root / "scripts/ci/required-prose.txt"
                    entries = [
                        line.strip()
                        for line in manifest.read_text(encoding="utf-8").splitlines()
                        if line.strip()
                    ]

                    if not entries:
                        raise ValueError("required prose manifest is empty")

                    if len(entries) != len(set(entries)):
                        raise ValueError("duplicate required prose path")

                    paths = []
                    for name in entries:
                        relative = Path(name)

                        if (
                            relative.is_absolute()
                            or ".." in relative.parts
                            or relative.suffix != ".md"
                        ):
                            raise ValueError(f"invalid required prose path: {name}")

                        path = root / relative

                        if not path.resolve().is_relative_to(root.resolve()):
                            raise ValueError(
                                f"required prose path escapes root: {name}"
                            )

                        if not path.is_file():
                            raise ValueError(f"missing required prose document: {name}")

                        paths.append(path)

                    return paths
