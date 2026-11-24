"""Load a narrow key=value specimen without duplicate keys."""

from pathlib import Path


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
