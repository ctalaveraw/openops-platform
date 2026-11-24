"""Validate packaging source rules without building an image."""

import unittest

from scripts import verify

ROOT = verify.ROOT


class PackagingSourceTests(unittest.TestCase):
    def test_dockerfile_keeps_the_small_source_contract(self) -> None:
        def check_source(source: str) -> None:
            lines = [
                line.strip()
                for line in source.splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            ]
            self.assertEqual(len(lines), 4)
            self.assertRegex(
                lines[0],
                r"^FROM nginx/nginx-unprivileged:stable-alpine@sha256:[a-f0-9]{64}$",
            )
            self.assertEqual(
                lines[1], 'LABEL org.opencontainers.image.title="OpenOps Hello World"'
            )
            self.assertEqual(
                lines[2:], ["COPY public/ /usr/share/nginx/html/", "EXPOSE 8080"]
            )

        source = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        check_source(source)
        with self.assertRaises(AssertionError):
            check_source(source.replace("COPY public/", "COPY ./"))

    def test_dockerignore_declares_the_expected_exclusions(self) -> None:
        # Literal specimen contract, not a Docker pattern-matching engine.
        rules = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            set(rules),
            {
                ".git/",
                "docs/",
                "fixtures/",
                "schemas/",
                "contracts/",
                "l10n/",
                "scripts/",
                "tests/",
                "__pycache__/",
                "*.md",
                "Makefile",
                "compose.yaml",
                "VERSION",
            },
        )
