#!/usr/bin/env python3
"""Optional schema and YAML contract checks. No services are contacted."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_compose(document: dict, component: dict) -> None:
    port = component["runtime"]["port"]
    expected = {
        "services": {
            component["name"]: {
                "build": ".",
                "image": "openops-hello-world:local",
                "ports": [f"127.0.0.1:{port}:{port}"],
            }
        }
    }
    if document != expected:
        raise ValueError("compose.yaml: changed local service contract")


def check_openapi(document: dict, component: dict) -> None:
    runtime = component["runtime"]
    health = (ROOT / runtime["directory"] / "healthz").read_text().strip()
    version = (ROOT / component["versionFile"]).read_text().strip()
    expected = {
        runtime["healthPath"]: {
            "get": {
                "responses": {
                    "200": {
                        "description": "Static health response",
                        "content": {
                            "text/plain": {
                                "schema": {"type": "string", "const": health}
                            }
                        },
                    }
                }
            }
        }
    }
    if (
        document.get("openapi") != "3.1.0"
        or document["info"]["version"] != version
        or document.get("paths") != expected
    ):
        raise ValueError("openapi.yaml: changed static health contract")


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

    def load(path: str) -> dict:
        content = (ROOT / path).read_text(encoding="utf-8")
        return (
            yaml.safe_load(content)
            if path.endswith(".yaml")
            else json.loads(content)
        )

    try:
        episode = load("fixtures/hello.json")
        workload = load("contracts/workload.yaml")
        component = load("contracts/component.json")
        invalid_episode = {"episode": {**episode["episode"], "status": "broken"}}
        invalid_workload = {**workload, "containerPort": 0}
        invalid_component = load("fixtures/invalid/component.json")

        for schema, good, bad in (
            ("hello", episode, invalid_episode),
            ("workload", workload, invalid_workload),
            ("component", component, invalid_component),
        ):
            contract = load(f"schemas/{schema}.schema.json")
            jsonschema.Draft202012Validator.check_schema(contract)
            validator = jsonschema.Draft202012Validator(contract)
            validator.validate(good)
            if validator.is_valid(bad):
                raise ValueError(f"{schema}: invalid document passed validation")

        xsd = etree.XMLSchema(etree.parse(str(ROOT / "schemas/hello.xsd")))
        xsd.assertValid(etree.parse(str(ROOT / "fixtures/hello.xml")))
        invalid_xml = etree.fromstring(b"<episode><id>001</id></episode>")
        if xsd.validate(invalid_xml):
            raise ValueError("hello.xsd: incomplete episode passed validation")

        compose = load("compose.yaml")
        openapi = load("contracts/openapi.yaml")
        for check, good, bad in (
            (check_compose, compose, {"services": {}}),
            (check_openapi, openapi, {**openapi, "paths": {}}),
        ):
            check(good, component)
            try:
                check(bad, component)
            except ValueError:
                pass
            else:
                raise ValueError(f"{check.__name__}: invalid contract passed")
    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        jsonschema.ValidationError,
        jsonschema.SchemaError,
        yaml.YAMLError,
        etree.LxmlError,
    ) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: three JSON schemas and XSD accept good and reject bad documents")
    print("PASS: Compose and OpenAPI specimen contracts reject bad inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
