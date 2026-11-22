#!/usr/bin/env python3
"""Validate a CI event, preview its message, or send it to a configured Zulip bot."""

import argparse
import base64
import configparser
import http.client
import json
import math
import os
import re
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# Keep this command usable with the repository's Python, without a new service
# or additional packages. The future CI workflow calls this same entry point.
MAX_INPUT_BYTES = 16_384
MAX_RESPONSE_BYTES = 65_536
REQUEST_TIMEOUT = 10
MAX_ATTEMPTS = 3
MAX_RETRY_DELAY = 10


class InputError(Exception):
    """The caller supplied an invalid event or bot configuration."""


class DeliveryError(Exception):
    """Zulip did not confirm delivery; callers must preserve the CI result."""


@dataclass(frozen=True)
class Event:
    provider: str
    kind: str
    repository: str
    workflow: str
    revision: str
    severity: str
    event_id: str
    evidence_url: str
    channel: str
    topic: str
    recovery_of: str | None = None


@dataclass(frozen=True, repr=False)
class BotConfig:
    # Suppress the generated repr so accidental debug output does not expose keys.
    site: str
    email: str
    key: str


def text_field(data: dict, name: str, limit: int) -> str:
    value = data.get(name)
    if not isinstance(value, str) or not value or value != value.strip():
        raise InputError(f"{name} must be a nonempty string without edge whitespace")
    if len(value) > limit or any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise InputError(f"{name} must be a single line of at most {limit} characters")
    return value


def https_url(value: str, *, organization: bool = False) -> str:
    """Accept a credential-free HTTPS URL; an organization URL must be an origin."""
    try:
        parts = urllib.parse.urlsplit(value)
        port = parts.port  # Reading this property also validates the port number.
        hostname = parts.hostname
    except ValueError:
        raise InputError("URL has an invalid host or port") from None
    if (
        parts.scheme != "https"
        or not hostname
        or parts.username is not None
        or parts.password is not None
        or parts.query
        or parts.fragment
        or any(char.isspace() or char in '<>\\"`' for char in value)
    ):
        raise InputError("URL must use HTTPS without credentials, query or fragment")
    if organization and parts.path not in ("", "/"):
        raise InputError("Organization URL must not contain an application path")
    if organization:
        host = f"[{hostname}]" if ":" in hostname else hostname
        authority = host if port in (None, 443) else f"{host}:{port}"
        return f"https://{authority}"
    return value


def parse_event(data: object) -> Event:
    """Normalize GitHub and Forgejo producers' common event envelope."""
    if not isinstance(data, dict):
        raise InputError("Event must be a JSON object")
    required = {
        "schema_version",
        "source",
        "provider",
        "event",
        "repository",
        "workflow",
        "revision",
        "severity",
        "idempotency_key",
        "evidence_url",
        "destination",
    }
    if required - data.keys() or data.keys() - required - {"recovery_of"}:
        raise InputError("Event fields do not match schema version 1")
    # bool is a subclass of int in Python; reject true instead of accepting it as 1.
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise InputError("schema_version must be the integer 1")
    if data["source"] != "ci" or data["provider"] not in ("github", "forgejo"):
        raise InputError("source must be ci and provider must be github or forgejo")
    kind = data["event"]
    if kind not in ("validation_failed", "validation_recovered"):
        raise InputError("event must be validation_failed or validation_recovered")
    severity = data["severity"]
    allowed = ("warning", "error") if kind == "validation_failed" else ("info",)
    if severity not in allowed:
        raise InputError("severity does not match the event result")
    destination = data["destination"]
    if not isinstance(destination, dict) or set(destination) != {"channel", "topic"}:
        raise InputError("destination must contain channel and topic only")
    revision = text_field(data, "revision", 64)
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", revision):
        raise InputError("revision must be a full lowercase Git commit ID")
    recovery_of = None
    if kind == "validation_recovered":
        recovery_of = text_field(data, "recovery_of", 200)
    elif "recovery_of" in data:
        raise InputError("Only a recovery event may contain recovery_of")
    event_id = text_field(data, "idempotency_key", 200)
    if recovery_of == event_id:
        raise InputError("A recovery must reference a different event ID")
    return Event(
        provider=data["provider"],
        kind=kind,
        repository=text_field(data, "repository", 120),
        workflow=text_field(data, "workflow", 120),
        revision=revision,
        severity=severity,
        event_id=event_id,
        evidence_url=https_url(text_field(data, "evidence_url", 2048)),
        channel=text_field(destination, "channel", 80),
        topic=text_field(destination, "topic", 60),
        recovery_of=recovery_of,
    )


def read_event(path: Path) -> Event:
    try:
        with path.open("rb") as source:
            content = source.read(MAX_INPUT_BYTES + 1)
        if len(content) > MAX_INPUT_BYTES:
            raise InputError("Event file exceeds 16 KiB")
        data = json.loads(content.decode("utf-8"), object_pairs_hook=unique_fields)
    except (OSError, UnicodeError, ValueError, RecursionError):
        # Do not echo raw input: an invalid file might contain private material.
        raise InputError("Could not read a UTF-8 JSON event file") from None
    return parse_event(data)


def unique_fields(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("Event contains a duplicate JSON field")
        result[key] = value
    return result


def code_span(value: str) -> str:
    # A longer backtick fence keeps embedded Markdown and @mentions literal.
    longest = max((len(match) for match in re.findall(r"`+", value)), default=0)
    fence = "`" * (longest + 1)
    return f"{fence} {value} {fence}" if longest else f"{fence}{value}{fence}"


def message_payload(event: Event) -> dict:
    status = (
        ":warning: **CI failed**"
        if event.kind == "validation_failed"
        else ":check: **CI recovered**"
    )
    # Parentheses in an evidence URL must not close the Markdown link early.
    link = urllib.parse.quote(event.evidence_url, safe=":/[]@!$&'*,;=+%~._-")
    lines = [
        f"{status} · {code_span(event.workflow)}",
        f"{code_span(event.repository)} · revision {code_span(event.revision[:12])} · "
        f"[View run]({link})",
        f"Event {code_span(event.event_id)}",
    ]
    if event.recovery_of is not None:
        lines.append(f"Recovers {code_span(event.recovery_of)}")
    return {
        "type": "stream",
        "to": event.channel,
        "topic": event.topic,
        "content": "\n".join(lines),
    }


def read_config(path: Path, expected_site: str) -> BotConfig:
    try:
        with path.open("rb") as source:
            info = os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_INPUT_BYTES:
                raise InputError("Bot configuration must be a small regular file")
            if sys.platform != "win32" and stat.S_IMODE(info.st_mode) & 0o077:
                raise InputError(
                    "Bot configuration must be private; set its mode to 0600"
                )
            content = source.read(MAX_INPUT_BYTES + 1)
            if len(content) > MAX_INPUT_BYTES:
                raise InputError("Bot configuration exceeds 16 KiB")
        # Disable interpolation: a literal % in an API key is not a substitution.
        parser = configparser.ConfigParser(interpolation=None)
        parser.read_string(content.decode("utf-8"))
        values = {name: parser.get("api", name) for name in ("site", "email", "key")}
    except (OSError, UnicodeError, configparser.Error):
        raise InputError(
            "Could not read bot configuration with [api] site, email and key"
        ) from None
    site = https_url(text_field(values, "site", 2048), organization=True)
    if site != https_url(expected_site, organization=True):
        raise InputError(
            "Bot configuration site does not match the intended organization"
        )
    email = text_field(values, "email", 254)
    if ":" in email:
        raise InputError("Bot email must not contain a colon")
    return BotConfig(site=site, email=email, key=text_field(values, "key", 512))


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward a bot's Authorization header to a redirected origin.
        return None


def retry_delay(error: urllib.error.HTTPError, attempt: int) -> float:
    delay = error.headers.get("Retry-After") if error.headers is not None else None
    if delay is None:
        try:
            content = error.read(MAX_RESPONSE_BYTES + 1)
            if len(content) > MAX_RESPONSE_BYTES:
                raise DeliveryError("Rate-limit response exceeds 64 KiB; try later")
            response = json.loads(content, object_pairs_hook=unique_fields)
            if isinstance(response, dict):
                delay = response.get("retry-after")
        except (ValueError, UnicodeError):
            pass
        except (InputError, RecursionError):
            raise DeliveryError("Invalid rate-limit response; try later") from None
        except (OSError, http.client.HTTPException):
            raise DeliveryError(
                "Could not read the rate-limit response; try later"
            ) from None
    if delay is None:
        return float(2 ** (attempt - 1))
    if isinstance(delay, bool):
        raise DeliveryError("Rate-limit delay must be numeric; try later")
    try:
        seconds = float(delay)
    except (TypeError, ValueError):
        raise DeliveryError(
            "Rate limited with an unsupported Retry-After; try later"
        ) from None
    if not math.isfinite(seconds) or seconds < 0 or seconds > MAX_RETRY_DELAY:
        raise DeliveryError(
            "Rate-limit delay exceeds this command's retry budget; try later"
        )
    return seconds


def send_message(
    event: Event, config: BotConfig, *, opener=None, sleep=time.sleep
) -> int:
    opener = opener or urllib.request.build_opener(NoRedirects())
    authorization = base64.b64encode(f"{config.email}:{config.key}".encode()).decode(
        "ascii"
    )
    payload = urllib.parse.urlencode(message_payload(event)).encode("utf-8")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        request = urllib.request.Request(
            config.site + "/api/v1/messages",
            data=payload,
            headers={
                "Authorization": "Basic " + authorization,
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "OpenOps-Zulip-Notifier/1",
            },
            method="POST",
        )
        try:
            with opener.open(request, timeout=REQUEST_TIMEOUT) as response:
                content = response.read(MAX_RESPONSE_BYTES + 1)
                if (
                    not 200 <= response.status < 300
                    or len(content) > MAX_RESPONSE_BYTES
                ):
                    raise DeliveryError(
                        "Unexpected response; delivery is unconfirmed. "
                        "Inspect chat before retrying."
                    )
            try:
                result = json.loads(content, object_pairs_hook=unique_fields)
            except (ValueError, UnicodeError, InputError, RecursionError):
                raise DeliveryError(
                    "Invalid response; delivery is unconfirmed. "
                    "Inspect chat before retrying."
                ) from None
            if (
                not isinstance(result, dict)
                or result.get("result") != "success"
                or type(result.get("id")) is not int
                or result["id"] <= 0
            ):
                raise DeliveryError(
                    "Missing success acknowledgement; inspect chat before retrying"
                )
            return result["id"]
        except urllib.error.HTTPError as error:
            try:
                if error.code == 429 and attempt < MAX_ATTEMPTS:
                    delay = retry_delay(error, attempt)
                elif error.code == 429:
                    raise DeliveryError(
                        "Rate limited after three attempts; try later"
                    ) from None
                elif 300 <= error.code < 400:
                    raise DeliveryError(
                        "Redirect refused; verify the configured organization URL"
                    ) from None
                elif 400 <= error.code < 500:
                    raise DeliveryError(
                        f"Zulip rejected delivery (HTTP {error.code})"
                    ) from None
                else:
                    raise DeliveryError(
                        f"Delivery unconfirmed (HTTP {error.code}); "
                        "inspect chat before retrying"
                    ) from None
            finally:
                error.close()
            # Retry only a known rejection. A timeout or 5xx may occur after
            # Zulip accepted the message; automatically resending risks duplicates.
            sleep(delay)
        except (OSError, urllib.error.URLError, http.client.HTTPException):
            raise DeliveryError(
                "Connection failed; delivery is unconfirmed. "
                "Inspect chat before retrying."
            ) from None
    raise DeliveryError("Delivery was not confirmed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--event", type=Path, required=True, help="version 1 CI event JSON file"
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="send instead of previewing; may post to chat",
    )
    parser.add_argument("--config", type=Path, help="private downloaded zuliprc file")
    parser.add_argument(
        "--site", help="intended collaboration organization HTTPS origin"
    )
    parser.add_argument(
        "--channel", help="approved destination channel; must match the event"
    )
    args = parser.parse_args(argv)
    if args.send and not all((args.config, args.site, args.channel)):
        parser.error("--send requires --config, --site and --channel")
    try:
        event = read_event(args.event)
        if not args.send:
            # Previewing never reads credentials or constructs a network client.
            print(json.dumps(message_payload(event), indent=2, ensure_ascii=False))
            return 0
        if event.channel != args.channel:
            raise InputError("Event channel does not match the approved destination")
        config = read_config(args.config, args.site)
        message_id = send_message(event, config)
        print(f"Zulip confirmed message {message_id}.")
        return 0
    except InputError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 2
    except DeliveryError as error:
        print(f"Notification failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
