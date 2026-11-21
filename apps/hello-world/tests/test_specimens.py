"""Independent specimens for platform tooling, not runtime application code."""

import configparser
import gzip
import re
import shlex
import sqlite3
import tarfile
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from scripts import verify

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
PROM_LINE = re.compile(r'openops_fixture_ready\{id="([^"]+)",status="([^"]+)"\} ([01])')


class FormatSpecimens(unittest.TestCase):
    def test_sqlite_runs_only_in_memory(self) -> None:
        connection = sqlite3.connect(":memory:")
        try:
            connection.executescript((FIXTURES / "hello.sql").read_text())
            row = connection.execute(
                "SELECT id, title, status FROM episodes"
            ).fetchone()
            self.assertEqual(dict(zip(verify.FIELDS, row)), verify.EXPECTED)
        finally:
            connection.close()

    def test_bad_sql_is_rejected(self) -> None:
        connection = sqlite3.connect(":memory:")
        try:
            with self.assertRaises(sqlite3.OperationalError):
                connection.executescript((FIXTURES / "invalid/bad.sql").read_text())
        finally:
            connection.close()

    def test_prometheus_specimen(self) -> None:
        lines = (FIXTURES / "hello.prom").read_text().splitlines()
        self.assertTrue(lines[0].startswith("# HELP openops_fixture_ready "))
        self.assertEqual(lines[1], "# TYPE openops_fixture_ready gauge")
        match = PROM_LINE.fullmatch(lines[2])
        self.assertIsNotNone(match)
        self.assertEqual(match.groups(), ("001", "ready", "1"))
        self.assertEqual(len(lines), 3)

    def test_bad_metric_is_rejected(self) -> None:
        line = (FIXTURES / "invalid/bad.prom").read_text().splitlines()[1]
        self.assertIsNone(PROM_LINE.fullmatch(line))

    def test_http_request_examples(self) -> None:
        lines = (FIXTURES / "hello.http").read_text().splitlines()
        requests = [line for line in lines if line.startswith("GET ")]
        self.assertEqual(
            requests,
            [
                "GET http://127.0.0.1:8080/healthz HTTP/1.1",
                "GET http://127.0.0.1:8080/version.txt HTTP/1.1",
            ],
        )
        for path in ("healthz", "version.txt"):
            self.assertTrue((ROOT / "public" / path).is_file())
        self.assertIn(
            "containerPort: 8080",
            (ROOT / "contracts/workload.yaml").read_text(),
        )

    def test_env_example_matches_episode(self) -> None:
        values = {}
        for line in (FIXTURES / "hello.env.example").read_text().splitlines():
            if line.startswith("#"):
                continue
            key, raw = line.split("=", 1)
            self.assertRegex(key, r"^HELLO_[A-Z]+$")
            self.assertNotIn(key, values)
            items = shlex.split(raw)
            self.assertEqual(len(items), 1)
            values[key.removeprefix("HELLO_").lower()] = items[0]
        self.assertEqual(values, verify.EXPECTED)

    def test_rss_example(self) -> None:
        rss = ET.parse(FIXTURES / "hello.rss.xml").getroot()
        self.assertEqual(rss.tag, "rss")
        self.assertEqual(rss.attrib, {"version": "2.0"})
        channel = rss.find("channel")
        self.assertIsNotNone(channel)
        self.assertEqual(channel.findtext("link"), "https://example.invalid/")
        item = channel.find("item")
        self.assertIsNotNone(item)
        self.assertEqual(item.findtext("title"), verify.EXPECTED["title"])
        self.assertEqual(item.findtext("guid"), verify.EXPECTED["id"])
        self.assertEqual(item.findtext("description"), verify.EXPECTED["status"])

    def test_log_example(self) -> None:
        parts = (FIXTURES / "hello.log").read_text().strip().split(" ")
        timestamp = datetime.fromisoformat(parts[0].replace("Z", "+00:00"))
        self.assertEqual(timestamp.year, 2026)
        self.assertEqual(parts[1], "INFO")
        self.assertEqual(parts[2:], ["episode=001", "status=ready"])

    def test_local_editor_settings(self) -> None:
        parser = configparser.ConfigParser(interpolation=None)
        parser.read_string("[DEFAULT]\n" + (ROOT / ".editorconfig").read_text())
        self.assertEqual(parser.get("*", "charset"), "utf-8")
        self.assertEqual(parser.get("*", "end_of_line"), "lf")
        self.assertEqual(parser.get("Makefile", "indent_style"), "tab")
        attributes = (ROOT / ".gitattributes").read_text()
        self.assertIn("*.sql text eol=lf", attributes)
        self.assertIn("*.xml text eol=lf", attributes)

    def test_documented_graph(self) -> None:
        graph = (FIXTURES / "hello.dot").read_text()
        self.assertIn("digraph hello {", graph)
        self.assertIn("source -> check;", graph)
        self.assertIn("check -> image [style=dashed];", graph)

    def test_archive_round_trip_without_persistent_artifacts(self) -> None:
        # An actual archive round-trip, but no committed/generated build artifact.
        data = (FIXTURES / "hello.csv").read_bytes()
        self.assertEqual(gzip.decompress(gzip.compress(data)), data)
        with tempfile.TemporaryFile() as output:
            with tarfile.open(fileobj=output, mode="w") as archive:
                archive.add(FIXTURES / "hello.csv", arcname="hello.csv")
            output.seek(0)
            with tarfile.open(fileobj=output, mode="r") as archive:
                self.assertEqual(archive.extractfile("hello.csv").read(), data)


if __name__ == "__main__":
    unittest.main()
