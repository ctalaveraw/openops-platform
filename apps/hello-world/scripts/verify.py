#!/usr/bin/env python3
"""Verify the static page and one episode stored in several data formats."""

import configparser
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from checks.formats import load_all_formats
from checks.formats.contract import EXPECTED
from checks.formats.validate_csv import load_delimited as load_delimited
from checks.formats.validate_properties import load_properties as load_properties
from checks.formats.validate_xml import load_xml as load_xml
from checks.formats.validate_yaml import load_fixture_yaml as load_fixture_yaml
from checks.validate_manifest import validate_manifest
from checks.validate_svg import validate_svg

ROOT = Path(__file__).resolve().parents[1]
FIELDS = tuple(EXPECTED)


def load_episode_formats() -> dict[str, dict[str, str]]:
    return load_all_formats(ROOT)


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
    version = (ROOT / "VERSION").read_text(encoding="utf-8")
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:[.](?:0|[1-9][0-9]*)){2}\n", version):
        raise ValueError("VERSION: expected three numeric version fields")
    if (ROOT / "public/version.txt").read_text(encoding="utf-8") != version:
        raise ValueError("version.txt: differs from VERSION")
    if (ROOT / "public/robots.txt").read_text(encoding="utf-8") != (
        "User-agent: *\nDisallow:\n"
    ):
        raise ValueError("robots.txt: unexpected content")
    validate_manifest(ROOT / "public/site.webmanifest")
    validate_svg(ROOT / "public/favicon.svg")
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
    except (
        OSError,
        configparser.Error,
        ValueError,
        KeyError,
        TypeError,
        ET.ParseError,
        json.JSONDecodeError,
    ) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: page assets, schemas parsed, nine data formats agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
