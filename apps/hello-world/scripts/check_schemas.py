#!/usr/bin/env python3
"""Optional full schema checks; dependencies are dev tools, not app runtime."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        import jsonschema
        import yaml
        from lxml import etree
    except ImportError:
        print(
            "Requires jsonschema, PyYAML and lxml (optional developer tools).",
            file=sys.stderr,
        )
        return 2

    for document, schema in (
        ("fixtures/hello.json", "schemas/hello.schema.json"),
        ("contracts/workload.yaml", "schemas/workload.schema.json"),
    ):
        content = (ROOT / document).read_text(encoding="utf-8")
        data = (
            yaml.safe_load(content)
            if document.endswith(".yaml")
            else json.loads(content)
        )
        contract = json.loads((ROOT / schema).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(contract)
        jsonschema.validate(data, contract)
    xsd = etree.XMLSchema(etree.parse(str(ROOT / "schemas/hello.xsd")))
    if not xsd.validate(etree.parse(str(ROOT / "fixtures/hello.xml"))):
        print("FAIL: hello.xml does not match hello.xsd", file=sys.stderr)
        return 1
    print("PASS: JSON Schema, YAML contract and XSD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
