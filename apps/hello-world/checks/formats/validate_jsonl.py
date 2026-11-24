"""Load the single-record JSONL specimen."""

import json
from pathlib import Path


def load_jsonl(path: Path) -> dict[str, str]:
    return json.loads(path.read_text(encoding="utf-8"))
