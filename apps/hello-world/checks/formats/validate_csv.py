"""Load the specimen CSV and TSV; both share a record layout."""

import csv
from pathlib import Path

from checks.formats.contract import FIELDS


def load_delimited(path: Path, delimiter: str) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=delimiter)
        if reader.fieldnames != list(FIELDS):
            raise ValueError(f"{path.name}: expected columns {FIELDS}")
        rows = list(reader)
    if len(rows) != 1 or any(
        set(row) != set(FIELDS) or None in row.values() for row in rows
    ):
        raise ValueError(f"{path.name}: expected one complete episode, no duplicates")
    return rows[0]


def load_csv(path: Path) -> dict[str, str]:
    return load_delimited(path, ",")


def load_tsv(path: Path) -> dict[str, str]:
    return load_delimited(path, "\t")
