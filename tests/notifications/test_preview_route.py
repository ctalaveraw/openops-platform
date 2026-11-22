"""Check proposed routing without credentials, HTTP, or event-file changes."""

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts.notifications import notify_zulip as notify
from scripts.notifications import preview_route as route

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples/notifications"
SCRIPT = ROOT / "scripts/notifications/preview_route.py"


def fixture(provider="github"):
    return json.loads((EXAMPLES / f"{provider}-failure.json").read_text())


class RoutingTests(unittest.TestCase):
    def test_same_pr_number_has_distinct_provider_topics(self):
        topics = []
        for provider in ("github", "forgejo"):
            event = notify.parse_event(fixture(provider))
            payload = route.pr_payload(event, 123)
            self.assertEqual(
                payload["topic"], f"{provider} example/openops-platform PR #123"
            )
            self.assertEqual(payload["to"], "development-events")
            self.assertIn(event.evidence_url, payload["content"])
            self.assertIn(event.event_id, payload["content"])
            topics.append(payload["topic"])
        self.assertNotEqual(*topics)

    def test_repository_and_pr_number_both_distinguish_topics(self):
        original = notify.parse_event(fixture())
        another = fixture()
        another["repository"] = "example/another-platform"
        topics = {
            route.pr_payload(original, 123)["topic"],
            route.pr_payload(original, 124)["topic"],
            route.pr_payload(notify.parse_event(another), 123)["topic"],
        }
        self.assertEqual(len(topics), 3)

    def test_failure_and_recovery_keep_one_topic_and_distinct_event_ids(self):
        failed = fixture()
        recovered = fixture()
        recovered.update(
            event="validation_recovered",
            severity="info",
            idempotency_key="opaque-recovery-id",
            recovery_of=failed["idempotency_key"],
        )
        failure = route.pr_payload(notify.parse_event(failed), 123)
        recovery = route.pr_payload(notify.parse_event(recovered), 123)
        self.assertEqual(failure["topic"], recovery["topic"])
        self.assertIn("**CI recovered**", recovery["content"])
        self.assertIn("Event `opaque-recovery-id`", recovery["content"])
        self.assertIn(f"Recovers `{failed['idempotency_key']}`", recovery["content"])

    def test_preview_does_not_mutate_legacy_route_or_parse_event_id(self):
        data = fixture()
        data["idempotency_key"] = "opaque/keep-this-id"
        event = notify.parse_event(data)
        before = notify.message_payload(event)
        first = route.pr_payload(event, 123)
        self.assertEqual(first, route.pr_payload(event, 123))
        self.assertEqual(notify.message_payload(event), before)
        self.assertEqual(before["topic"], "CI / Repository checks")
        self.assertEqual(first["content"], before["content"])

    def test_invalid_pr_number_and_overlong_topic_are_rejected(self):
        event = notify.parse_event(fixture())
        for number in (True, 0, -1, "123", 1.5):
            with self.subTest(number=number), self.assertRaises(notify.InputError):
                route.pr_payload(event, number)
        data = fixture()
        data["repository"] = "example/" + "a" * 80
        with self.assertRaisesRegex(notify.InputError, "60 characters"):
            route.pr_payload(notify.parse_event(data), 123)

    def test_cli_preview_never_reads_config_or_constructs_transport(self):
        path = EXAMPLES / "github-failure.json"
        before = path.read_bytes()
        output = io.StringIO()
        with (
            patch.object(
                notify, "read_config", side_effect=AssertionError("config read")
            ),
            patch.object(
                notify, "send_message", side_effect=AssertionError("send attempted")
            ),
            patch.object(
                notify.urllib.request,
                "build_opener",
                side_effect=AssertionError("transport created"),
            ),
            redirect_stdout(output),
        ):
            self.assertEqual(
                route.main(["--event", str(path), "--pull-request", "123"]), 0
            )
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(
            json.loads(output.getvalue())["topic"],
            "github example/openops-platform PR #123",
        )

    def test_cli_rejects_send_flag_and_bad_pr_number(self):
        for extra in (["--send"], ["--pull-request", "zero"]):
            with self.subTest(extra=extra), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    route.main(
                        [
                            "--event",
                            str(EXAMPLES / "github-failure.json"),
                            "--pull-request",
                            "123",
                            *extra,
                        ]
                    )
                self.assertEqual(caught.exception.code, 2)

    def test_cli_rejects_malformed_event_without_echoing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "event.json"
            path.write_text('{"private-value":')
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                self.assertEqual(
                    route.main(["--event", str(path), "--pull-request", "123"]), 2
                )
            self.assertEqual(output.getvalue(), "")
            self.assertNotIn("private-value", errors.getvalue())

    def test_cli_runs_from_another_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--event",
                    str(EXAMPLES / "forgejo-failure.json"),
                    "--pull-request",
                    "123",
                ],
                cwd=directory,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout)["topic"],
            "forgejo example/openops-platform PR #123",
        )


if __name__ == "__main__":
    unittest.main()
