"""Load the single XML episode specimen."""

import xml.etree.ElementTree as ET
from pathlib import Path

from checks.formats.contract import FIELDS


def load_xml(path: Path) -> dict[str, str]:
    root = ET.parse(path).getroot()
    if root.tag != "episode" or [node.tag for node in root] != list(FIELDS):
        raise ValueError(f"{path.name}: unexpected XML fields")
    return {node.tag: node.text or "" for node in root}
