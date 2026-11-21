#!/usr/bin/env python3
"""Verify the static page and one episode stored in several data formats."""

import configparser
import csv
import json
import re
import sys
import tomllib
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"id": "001", "title": "Hello, Ops World!", "status": "ready"}
FIELDS = tuple(EXPECTED)


def load_delimited(path: Path, delimiter: str) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=delimiter)
        if reader.fieldnames != list(FIELDS):
            raise ValueError(f"{path.name}: expected columns {FIELDS}")
        rows = list(reader)
    if len(rows) != 1 or any(set(row) != set(FIELDS) for row in rows):
        raise ValueError(f"{path.name}: expected one complete episode, no duplicates")
    return rows[0]


def load_xml(path: Path) -> dict[str, str]:
    root = ET.parse(path).getroot()
    if root.tag != "episode" or [node.tag for node in root] != list(FIELDS):
        raise ValueError(f"{path.name}: unexpected XML fields")
    return {node.tag: node.text or "" for node in root}


def load_properties(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            raise ValueError(f"{path.name}: expected key=value")
        key, value = line.split("=", 1)
        if key in result:
            raise ValueError(f"{path.name}: duplicate key {key}")
        result[key] = value
    return result


def load_fixture_yaml(path: Path) -> dict[str, str]:
    """Read only the three quoted fields in our specimen, not general YAML."""
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    if len(lines) != 4 or lines[0] != "episode:":
        raise ValueError(f"{path.name}: unexpected fixture layout")
    fields = {}
    for line in lines[1:]:
        match = re.fullmatch(r'  (id|title|status): "([^"\n]*)"', line)
        if match is None or match.group(1) in fields:
            raise ValueError(f"{path.name}: unexpected field")
        fields[match.group(1)] = match.group(2)
    return fields


def load_episode_formats() -> dict[str, dict[str, str]]:
    fixtures = ROOT / "fixtures"
    ini = configparser.ConfigParser(interpolation=None)
    with (fixtures / "hello.ini").open(encoding="utf-8") as stream:
        ini.read_file(stream)
    if ini.sections() != ["episode"]:
        raise ValueError("hello.ini: missing or extra section")
    return {
        "json": json.loads((fixtures / "hello.json").read_text(encoding="utf-8"))[
            "episode"
        ],
        "csv": load_delimited(fixtures / "hello.csv", ","),
        "tsv": load_delimited(fixtures / "hello.tsv", "\t"),
        "xml": load_xml(fixtures / "hello.xml"),
        "yaml": load_fixture_yaml(fixtures / "hello.yaml"),
        "toml": tomllib.loads((fixtures / "hello.toml").read_text(encoding="utf-8"))[
            "episode"
        ],
        "ini": dict(ini["episode"]),
        "jsonl": json.loads((fixtures / "hello.jsonl").read_text(encoding="utf-8")),
        "properties": load_properties(fixtures / "hello.properties"),
    }


class PageElements(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.links: dict[str, str] = {}
        self.headings: list[str] = []
        self._heading = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        attributes = dict(attrs)
        if tag == "link" and attributes.get("rel"):
            self.links[attributes["rel"] or ""] = attributes.get("href") or ""
        if tag == "h1":
            self._heading = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self._heading = False

    def handle_data(self, data: str) -> None:
        if self._heading:
            self.headings.append(data.strip())


def verify_static() -> None:
    page = PageElements()
    page.feed((ROOT / "public/index.html").read_text(encoding="utf-8"))
    if page.headings != ["Hello, Ops World! ✨"]:
        raise ValueError("index.html: banner heading changed")
    expected_links = {
        "stylesheet": "/style.css",
        "icon": "/favicon.svg",
        "manifest": "/site.webmanifest",
    }
    if not expected_links.items() <= page.links.items():
        raise ValueError("index.html: missing stylesheet, icon or manifest")
    for path in expected_links.values():
        if not (ROOT / "public" / path.lstrip("/")).is_file():
            raise ValueError(f"index.html: missing asset {path}")
    if any(tag in page.tags for tag in ("script", "iframe")):
        raise ValueError("index.html: unexpected scripted or embedded content")
    if (ROOT / "public/healthz").read_text(encoding="utf-8") != "ok\n":
        raise ValueError("healthz: expected 'ok' followed by newline")
    if (ROOT / "public/version.txt").read_text(encoding="utf-8") != (
        ROOT / "VERSION"
    ).read_text(encoding="utf-8"):
        raise ValueError("version.txt: differs from VERSION")
    if (ROOT / "public/robots.txt").read_text(encoding="utf-8") != (
        "User-agent: *\nDisallow:\n"
    ):
        raise ValueError("robots.txt: unexpected content")
    manifest = json.loads(
        (ROOT / "public/site.webmanifest").read_text(encoding="utf-8")
    )
    if manifest["icons"][0]["src"] != "/favicon.svg":
        raise ValueError("site.webmanifest: wrong icon")
    ET.parse(ROOT / "public/favicon.svg")
    ET.parse(ROOT / "schemas/hello.xsd")
    json.loads((ROOT / "schemas/hello.schema.json").read_text(encoding="utf-8"))
    json.loads((ROOT / "schemas/workload.schema.json").read_text(encoding="utf-8"))


def verify_formats() -> None:
    for name, values in load_episode_formats().items():
        if values != EXPECTED:
            raise ValueError(f"{name}: expected {EXPECTED!r}, found {values!r}")


def main() -> int:
    try:
        verify_static()
        verify_formats()
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: page assets, schemas parsed, nine data formats agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
