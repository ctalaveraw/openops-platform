#!/usr/bin/env python3
"""Evaluate local JSON Deployment fixtures; never contacts Kubernetes."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rules.deployment import inspect  # noqa: E402

VERSION = "openops-policy-report/v1"


def evaluate(path):
    result = {"version": VERSION, "file": str(path), "status": "error", "findings": []}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result["error"] = {"category": "parse", "message": str(exc)}
        return result

    if (
        not isinstance(document, dict)
        or document.get("apiVersion") != "apps/v1"
        or document.get("kind") != "Deployment"
    ):
        result["error"] = {
            "category": "unsupported",
            "message": "Expected an apps/v1 Deployment object",
        }
        return result

    metadata = document.get("metadata")
    spec = document.get("spec")
    if not isinstance(metadata, dict) or not isinstance(spec, dict):
        result["error"] = {
            "category": "structure",
            "message": "Deployment metadata and spec must be objects",
        }
        return result
    template = spec.get("template")
    if (
        not isinstance(template, dict)
        or not isinstance(template.get("metadata"), dict)
        or not isinstance(template.get("spec"), dict)
    ):
        result["error"] = {
            "category": "structure",
            "message": "Pod template metadata and spec must be objects",
        }
        return result
    pod_spec = template["spec"]
    containers = pod_spec.get("containers")
    if not isinstance(containers, list) or any(
        not isinstance(c, dict) for c in containers
    ):
        result["error"] = {
            "category": "structure",
            "message": "Pod containers must be a list of objects",
        }
        return result
    for obj in (metadata.get("labels", {}), template["metadata"].get("labels", {})):
        if not isinstance(obj, dict):
            result["error"] = {
                "category": "structure",
                "message": "Labels must be objects",
            }
            return result
    for container in containers:
        if not isinstance(container.get("securityContext", {}), dict):
            result["error"] = {
                "category": "structure",
                "message": "Container securityContext must be an object",
            }
            return result

    result["findings"] = inspect(document)
    result["status"] = "deny" if result["findings"] else "allow"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Offline OpenOps deployment policy exercise"
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("files", type=Path, nargs="+")
    args = parser.parse_args(argv)
    results = [evaluate(path) for path in args.files]
    if args.format == "json":
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for item in results:
            print(f"{item['status'].upper()} {item['file']}")
            for finding in item["findings"]:
                print(
                    f"  {finding['id']} {finding['path']}: {finding['message']}"
                )
            if item.get("error"):
                category = item["error"]["category"]
                message = item["error"]["message"]
                print(f"  {category}: {message}")
    if any(item["status"] == "error" for item in results):
        return 2
    return 1 if any(item["status"] == "deny" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
