"""Offline checks for a single-container Kubernetes Deployment specimen."""

import re

DIGEST = re.compile(r"^\S+@sha256:[0-9a-f]{64}$")
NAME_LABEL = "app.kubernetes.io/name"


def inspect(document):
    """Return policy findings. Caller validates the document's basic shape."""
    findings = []

    def fail(rule, path, message):
        findings.append({"id": rule, "path": path, "message": message})

    metadata = document.get("metadata", {})
    template = document.get("spec", {}).get("template", {})
    pod = template.get("spec", {})
    containers = pod.get("containers", [])
    name = metadata.get("name")
    labels = metadata.get("labels", {})
    pod_labels = template.get("metadata", {}).get("labels", {})

    if not isinstance(name, str) or not name.strip():
        fail("K8S-METADATA-001", "metadata.name", "Deployment name is required")
    if not name or labels.get(NAME_LABEL) != name:
        fail(
            "K8S-METADATA-001",
            f"metadata.labels.{NAME_LABEL}",
            "Name label must match Deployment name",
        )
    if not name or pod_labels.get(NAME_LABEL) != name:
        fail(
            "K8S-METADATA-001",
            f"spec.template.metadata.labels.{NAME_LABEL}",
            "Pod name label must match Deployment name",
        )

    if len(containers) != 1:
        fail(
            "K8S-SCOPE-001",
            "spec.template.spec.containers",
            "This specimen supports exactly one container",
        )
        return findings

    container = containers[0]
    image = container.get("image")
    if not isinstance(image, str) or not DIGEST.fullmatch(image):
        fail(
            "K8S-IMAGE-001",
            "spec.template.spec.containers[0].image",
            "Container image must use an immutable sha256 digest",
        )

    security = container.get("securityContext", {})
    if security.get("privileged") is True:
        fail(
            "K8S-PRIV-001",
            "spec.template.spec.containers[0].securityContext.privileged",
            "Privileged containers are forbidden",
        )
    if security.get("runAsNonRoot") is not True:
        fail(
            "K8S-PRIV-001",
            "spec.template.spec.containers[0].securityContext.runAsNonRoot",
            "Set runAsNonRoot to true",
        )

    for probe in ("readinessProbe", "livenessProbe"):
        value = container.get(probe, {})
        http = value.get("httpGet", {}) if isinstance(value, dict) else {}
        has_path = isinstance(http, dict) and isinstance(http.get("path"), str)
        has_port = isinstance(http, dict) and isinstance(http.get("port"), (int, str))
        if not has_path or not http["path"].startswith("/") or not has_port:
            fail(
                "K8S-HEALTH-001",
                f"spec.template.spec.containers[0].{probe}",
                "HTTP probe with path and port is required",
            )
        elif isinstance(http["port"], bool):
            fail(
                "K8S-HEALTH-001",
                f"spec.template.spec.containers[0].{probe}",
                "Probe port cannot be boolean",
            )

    return findings
