"""Dispatch the nine documented fixture formats using explicit paths."""

from pathlib import Path
from typing import Callable

from checks.formats.contract import EXPECTED
from checks.formats.validate_csv import load_csv, load_tsv
from checks.formats.validate_ini import load_ini
from checks.formats.validate_json import load_json
from checks.formats.validate_jsonl import load_jsonl
from checks.formats.validate_properties import load_properties
from checks.formats.validate_toml import load_toml
from checks.formats.validate_xml import load_xml
from checks.formats.validate_yaml import load_fixture_yaml

FORMAT_LOADERS: dict[str, tuple[str, Callable[[Path], dict[str, str]]]] = {
    "json": ("hello.json", load_json),
    "csv": ("hello.csv", load_csv),
    "tsv": ("hello.tsv", load_tsv),
    "xml": ("hello.xml", load_xml),
    "yaml": ("hello.yaml", load_fixture_yaml),
    "toml": ("hello.toml", load_toml),
    "ini": ("hello.ini", load_ini),
    "jsonl": ("hello.jsonl", load_jsonl),
    "properties": ("hello.properties", load_properties),
}


def load_one(root: Path, name: str) -> dict[str, str]:
    if name not in FORMAT_LOADERS:
        raise ValueError(f"unknown format: {name}")
    filename, loader = FORMAT_LOADERS[name]
    return loader(root / "fixtures" / filename)


def load_all_formats(root: Path) -> dict[str, dict[str, str]]:
    return {name: load_one(root, name) for name in FORMAT_LOADERS}


def check_format(root: Path, name: str) -> None:
    values = load_one(root, name)
    if values != EXPECTED:
        raise ValueError(f"{name}: expected {EXPECTED!r}, found {values!r}")
