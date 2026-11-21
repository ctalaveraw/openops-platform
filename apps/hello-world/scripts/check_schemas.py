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
        ("contracts/component.json", "schemas/component.schema.json"),
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
    # The invalid component sample must fail the same contract.
    invalid_path = ROOT / "fixtures/invalid/component.json"
    schema_path = ROOT / "schemas/component.schema.json"
    invalid = json.loads(invalid_path.read_text(encoding="utf-8"))
    component_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(invalid, component_schema)
    except jsonschema.ValidationError:
        pass
    else:
        print("FAIL: invalid component passed validation", file=sys.stderr)
        return 1

    xsd = etree.XMLSchema(etree.parse(str(ROOT / "schemas/hello.xsd")))
    if not xsd.validate(etree.parse(str(ROOT / "fixtures/hello.xml"))):
        print("FAIL: hello.xml does not match hello.xsd", file=sys.stderr)
        return 1
    print("PASS: JSON Schema, component contract, YAML and XSD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
