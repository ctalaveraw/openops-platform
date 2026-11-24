"""Load the strict INI episode specimen."""

import configparser
from pathlib import Path


def load_ini(path: Path) -> dict[str, str]:
    ini = configparser.ConfigParser(interpolation=None)
    with path.open(encoding="utf-8") as stream:
        ini.read_file(stream)
    if ini.sections() != ["episode"]:
        raise ValueError(f"{path.name}: missing or extra section")
    return dict(ini["episode"])
