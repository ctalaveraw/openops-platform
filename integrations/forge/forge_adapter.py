"""Read pull-request details from either forge and create a candidate event."""

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MAX_RESPONSE_BYTES = 65_536
TIMEOUT_SECONDS = 5
REVISION = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


class ForgeError(Exception):
    """Invalid input or an unconfirmed read-only API result."""


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def origin(value):
    """Require an HTTPS origin, never an embedded credential or URL path."""
    if not isinstance(value, str):
        raise ForgeError("API origin must be a string")
    try:
        parts = urllib.parse.urlsplit(value)
        port = parts.port
    except (TypeError, ValueError):
        raise ForgeError("invalid API origin") from None
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.path not in ("", "/")
        or parts.query
        or parts.fragment
        or any(c.isspace() or c in '<>\\"`' for c in value)
    ):
        raise ForgeError("API origin must be credential-free HTTPS")
    host = f"[{parts.hostname}]" if ":" in parts.hostname else parts.hostname
    suffix = f":{port}" if port not in (None, 443) else ""
    return f"https://{host}{suffix}"


def parameters(provider, repository, number, site=None):
    if provider not in ("github", "forgejo"):
        raise ForgeError("provider must be github or forgejo")
    if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository):
        raise ForgeError("repository must be owner/name")
    if type(number) is not int or number < 1:
        raise ForgeError("pull request number must be a positive integer")
    if provider == "github":
        if site is not None and origin(site) != "https://github.com":
            raise ForgeError("GitHub site must be https://github.com")
        return "https://github.com", "https://api.github.com"
    if site is None:
        raise ForgeError("Forgejo site is required")
    forge = origin(site)
    return forge, forge


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ForgeError("duplicate JSON field")
        result[key] = value
    return result


def normalize(provider, repository, number, payload, *, site=None):
    """Return a deterministic candidate CloudEvents PR snapshot, not a webhook event."""
    web, _ = parameters(provider, repository, number, site)
    if not isinstance(payload, dict):
        raise ForgeError("pull request response must be an object")
    if type(payload.get("number")) is not int or payload["number"] != number:
        raise ForgeError("pull request number does not match request")
    head = payload.get("head")
    sha = head.get("sha") if isinstance(head, dict) else None
    if not isinstance(sha, str) or not REVISION.fullmatch(sha):
        raise ForgeError("head.sha must be a full lowercase Git revision")
    state = payload.get("state")
    if state not in ("open", "closed"):
        raise ForgeError("unsupported pull request state")
    merged_at = payload.get("merged_at")
    if merged_at is not None and (
        not isinstance(merged_at, str) or not merged_at or state != "closed"
    ):
        raise ForgeError("merged_at requires a closed PR and a timestamp string")
    status = "merged" if merged_at is not None else state
    endpoint = "pull" if provider == "github" else "pulls"
    url = f"{web}/{repository}/{endpoint}/{number}"
    if payload.get("html_url") != url:
        raise ForgeError("pull request URL does not match requested repository")
    # Snapshot identity is stable across repeated reads of unchanged metadata.
    identity = f"{provider}:{repository}:pull/{number}:{status}:{sha}"
    event_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return {
        "specversion": "1.0",
        "id": event_id,
        "source": f"{web}/{repository}",
        "type": "dev.openops.forge.pull_request.snapshot.v1",
        "subject": f"pulls/{number}",
        "datacontenttype": "application/json",
        "data": {
            "schema_version": 1,
            "provider": provider,
            "repository": repository,
            "number": number,
            "state": status,
            "revision": sha,
            "logical_change": f"{repository}@{sha}",
            "url": url,
        },
    }


def fetch_pull_request(provider, repository, number, *, site=None, opener=None):
    """GET a public PR using an injectable opener; no auth or writes."""
    _, api = parameters(provider, repository, number, site)
    prefix = "" if provider == "github" else "/api/v1"
    url = f"{api}{prefix}/repos/{repository}/pulls/{number}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "OpenOps-Forge-ReadOnly/0",
        },
        method="GET",
    )
    opener = (
        opener if opener is not None else urllib.request.build_opener(NoRedirects())
    )
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise ForgeError(f"unexpected HTTP {response.status}")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        code = exc.code
        exc.close()
        raise ForgeError(f"forge read failed (HTTP {code})") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ForgeError("forge read failed (network error)") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ForgeError("forge response exceeds 64 KiB")
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs)
    except (ValueError, UnicodeError):
        raise ForgeError("invalid UTF-8 JSON response") from None
    return normalize(provider, repository, number, payload, site=site)


def main(argv=None):
    """Preview a normalized PR snapshot from a local response fixture only."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=("github", "forgejo"))
    parser.add_argument("--repository", required=True)
    parser.add_argument("--number", type=int, required=True)
    parser.add_argument("--site", help="required for Forgejo; HTTPS origin")
    parser.add_argument("--fixture", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        with args.fixture.open("rb") as handle:
            raw = handle.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ForgeError("fixture exceeds 64 KiB")
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs)
        event = normalize(
            args.provider, args.repository, args.number, payload, site=args.site
        )
    except (OSError, UnicodeError, ValueError, ForgeError) as exc:
        detail = str(exc) if isinstance(exc, ForgeError) else "unreadable JSON"
        print(f"invalid PR fixture: {detail}", file=sys.stderr)
        return 2
    print(json.dumps(event, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
