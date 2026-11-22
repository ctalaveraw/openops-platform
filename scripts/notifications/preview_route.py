#!/usr/bin/env python3
"""Preview a proposed PR topic using an existing v1 CI event; never send it."""

import argparse
import json
import sys
from pathlib import Path

if __package__:
    from . import notify_zulip as notify
else:
    import notify_zulip as notify


def pr_payload(event: notify.Event, number: int) -> dict:
    """Keep event identity and channel; propose an explicit provider/PR topic."""
    if type(number) is not int or number < 1:
        raise notify.InputError("pull-request must be a positive integer")
    topic = f"{event.provider} {event.repository} PR #{number}"
    # Fail rather than silently shorten names and collide with another topic.
    notify.text_field({"topic": topic}, "topic", 60)
    return {**notify.message_payload(event), "topic": topic}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", type=Path, required=True, help="v1 CI event file")
    parser.add_argument("--pull-request", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        payload = pr_payload(notify.read_event(args.event), args.pull_request)
    except notify.InputError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
