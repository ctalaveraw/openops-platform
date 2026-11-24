"""Load the TOML episode specimen."""

import tomllib
from pathlib import Path


def load_toml(path: Path) -> dict[str, str]:
    return tomllib.loads(path.read_text(encoding="utf-8"))["episode"]
