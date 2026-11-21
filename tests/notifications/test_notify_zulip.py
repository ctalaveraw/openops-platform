"""Exercise the notifier offline; credentials and HTTP responses are synthetic."""

import base64
import io
import json
import ssl
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
from pathlib import Path
from unittest.mock import Mock, patch

from scripts.notifications import notify_zulip as notify

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/notifications/github-failure.json"
SCRIPT = ROOT / "scripts/notifications/notify_zulip.py"


def fixture():
    return json.loads(EXAMPLE.read_text())


class Response(io.BytesIO):
    def __init__(self, body=b'{"result":"success","id":42}', status=200):
        super().__init__(body)
        self.status = status


class FakeOpener:
    """Replace HTTP entirely, recording what would have been sent."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def open(self, request, *, timeout):
        self.calls.append((request, timeout))
        result = self.outcomes.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def http_error(code, retry_after=None, body=b"{}"):
    headers = Message()
    if retry_after is not None:
        headers["Retry-After"] = retry_after
    headers["Location"] = "https://different.example.invalid/"
    return urllib.error.HTTPError(
        "https://chat.example.invalid/api/v1/messages",
        code,
        "server text must not be echoed",
        headers,
        io.BytesIO(body),
    )


class EventTests(unittest.TestCase):
    def test_both_producers_normalize_to_the_same_message_fields(self):
        github = notify.parse_event(fixture())
        forgejo = notify.read_event(
            ROOT / "examples/notifications/forgejo-failure.json"
        )
        for name in (
            "kind",
            "repository",
            "workflow",
            "revision",
            "severity",
            "channel",
            "topic",
        ):
            self.assertEqual(getattr(github, name), getattr(forgejo, name))
        for event in (github, forgejo):
            payload = notify.message_payload(event)
            self.assertEqual(payload["to"], "development-events")
            self.assertEqual(payload["topic"], "CI / Repository checks")
            self.assertIn("**CI failed**", payload["content"])
            self.assertIn(event.evidence_url, payload["content"])
            self.assertEqual(len(payload["content"].splitlines()), 3)

    def test_rejects_missing_unknown_or_wrongly_typed_fields(self):
        cases = []
        for name in fixture():
            data = fixture()
            del data[name]
            cases.append(data)
        for name, value in (
            ("schema_version", True),
            ("schema_version", 2),
            ("provider", "unknown"),
            ("source", "chat"),
            ("event", "validation_succeeded"),
            ("severity", "info"),
            ("workflow", 42),
            ("workflow", "line\nbreak"),
            ("workflow", " @all "),
            ("revision", "main"),
            ("idempotency_key", ""),
            ("destination", []),
        ):
            data = fixture()
            data[name] = value
            cases.append(data)
        extra = fixture()
        extra["api_key"] = "private-value"
        cases.append(extra)
        for data in cases:
            with self.subTest(fields=list(data)), self.assertRaises(notify.InputError):
                notify.parse_event(data)
        with self.assertRaises(notify.InputError):
            notify.parse_event([])

    def test_rejects_unsafe_evidence_links_and_invalid_destinations(self):
        for url in (
            "http://example.invalid/1",
            "javascript:alert(1)",
            "https://user:private@example.invalid/1",
            "https://example.invalid/?token=private",
            "https://example.invalid/1#fragment",
            "https://example.invalid/line\nbreak",
            "https://example.invalid:invalid/1",
        ):
            data = fixture()
            data["evidence_url"] = url
            with self.subTest(url=url), self.assertRaises(notify.InputError):
                notify.parse_event(data)
        for destination in (
            {"channel": "", "topic": "CI"},
            {"channel": "events", "topic": "x" * 61},
            {"channel": "events", "topic": "CI", "site": "elsewhere"},
        ):
            data = fixture()
            data["destination"] = destination
            with (
                self.subTest(destination=destination),
                self.assertRaises(notify.InputError),
            ):
                notify.parse_event(data)

    def test_recovery_requires_a_reference_to_a_different_failure(self):
        data = fixture()
        data.update(
            event="validation_recovered",
            severity="info",
            idempotency_key="github:123:2:recovery",
        )
        with self.assertRaises(notify.InputError):
            notify.parse_event(data)
        data["recovery_of"] = data["idempotency_key"]
        with self.assertRaises(notify.InputError):
            notify.parse_event(data)
        data["recovery_of"] = "github:123:1:failure"
        payload = notify.message_payload(notify.parse_event(data))
        self.assertIn("**CI recovered**", payload["content"])
        self.assertIn("Recovers `github:123:1:failure`", payload["content"])

    def test_message_quotes_markdown_mentions_and_link_delimiters(self):
        data = fixture()
        data["workflow"] = "`example` @**all**"
        data["evidence_url"] = "https://example.invalid/run/(1)"
        text = notify.message_payload(notify.parse_event(data))["content"]
        self.assertIn("`` `example` @**all** ``", text)
        self.assertIn("https://example.invalid/run/%281%29", text)

    def test_bad_json_duplicates_and_oversized_input_fail_without_echoing_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "event.json"
            for content in (
                b'{"secret":"private-value",',
                b"\xff",
                b'{"schema_version":1,"schema_version":1}',
                b"x" * (notify.MAX_INPUT_BYTES + 1),
            ):
                path.write_bytes(content)
                with (
                    self.subTest(size=len(content)),
                    self.assertRaises(notify.InputError) as caught,
                ):
                    notify.read_event(path)
                self.assertNotIn("private-value", str(caught.exception))


class ConfigTests(unittest.TestCase):
    def config_file(
        self, directory, *, site="https://chat.example.invalid/", mode=0o600
    ):
        path = Path(directory) / "bot-config"
        path.write_text(
            f"[api]\nsite={site}\nemail=ci@example.invalid\nkey=test-only-%key\n"
        )
        path.chmod(mode)
        return path

    def test_reads_downloaded_ini_without_interpolation_or_secret_repr(self):
        with tempfile.TemporaryDirectory() as directory:
            config = notify.read_config(
                self.config_file(directory), "https://chat.example.invalid:443"
            )
            self.assertEqual(config.site, "https://chat.example.invalid")
            self.assertEqual(config.key, "test-only-%key")
            self.assertNotIn(config.key, repr(config))
            self.assertNotIn(config.email, repr(config))

    def test_rejects_a_different_organization_or_insecure_site(self):
        with tempfile.TemporaryDirectory() as directory:
            for site in (
                "https://projects.example.invalid",
                "http://chat.example.invalid",
                "https://chat.example.invalid/api/v1/messages",
                "https://user:key@chat.example.invalid",
                "https://chat.example.invalid?key=value",
            ):
                with self.subTest(site=site), self.assertRaises(notify.InputError):
                    notify.read_config(
                        self.config_file(directory, site=site),
                        "https://chat.example.invalid",
                    )

    @unittest.skipIf(sys.platform == "win32", "POSIX permission check")
    def test_rejects_readable_credentials_and_leaves_permissions_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.config_file(directory, mode=0o644)
            with self.assertRaisesRegex(notify.InputError, "0600"):
                notify.read_config(path, "https://chat.example.invalid")
            self.assertEqual(path.stat().st_mode & 0o777, 0o644)

    def test_rejects_missing_or_malformed_config_without_printing_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing"
            with self.assertRaises(notify.InputError):
                notify.read_config(path, "https://chat.example.invalid")
            for content in (
                "private-value",
                "[api]\nkey=private-value\n",
                "[api]\nsite=\xff",
            ):
                path.write_text(content)
                path.chmod(0o600)
                with (
                    self.subTest(content=content),
                    self.assertRaises(notify.InputError) as caught,
                ):
                    notify.read_config(path, "https://chat.example.invalid")
                self.assertNotIn("private-value", str(caught.exception))


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.event = notify.parse_event(fixture())
        self.config = notify.BotConfig(
            "https://chat.example.invalid", "ci@example.invalid", "test-only-%key"
        )

    def test_posts_the_expected_zulip_form_with_header_authentication(self):
        opener = FakeOpener(Response())
        self.assertEqual(
            notify.send_message(self.event, self.config, opener=opener), 42
        )
        request, timeout = opener.calls[0]
        self.assertEqual(
            request.full_url, "https://chat.example.invalid/api/v1/messages"
        )
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(timeout, 10)
        auth = request.get_header("Authorization").removeprefix("Basic ")
        self.assertEqual(
            base64.b64decode(auth).decode(), "ci@example.invalid:test-only-%key"
        )
        form = urllib.parse.parse_qs(request.data.decode())
        self.assertEqual(form["to"], ["development-events"])
        self.assertEqual(form["topic"], ["CI / Repository checks"])
        self.assertEqual(form["type"], ["stream"])
        self.assertNotIn(self.config.key, request.full_url)
        self.assertNotIn(self.config.key, request.data.decode())

    def test_retries_only_rejected_rate_limits_and_honors_the_delay(self):
        for rejected in (
            http_error(429, "2"),
            http_error(429, body=b'{"retry-after":2}'),
        ):
            opener = FakeOpener(rejected, Response())
            sleep = Mock()
            self.assertEqual(
                notify.send_message(
                    self.event, self.config, opener=opener, sleep=sleep
                ),
                42,
            )
            sleep.assert_called_once_with(2)
            self.assertEqual(len(opener.calls), 2)

    def test_rate_limit_retries_and_waits_are_bounded(self):
        opener = FakeOpener(http_error(429), http_error(429), http_error(429))
        sleep = Mock()
        with self.assertRaisesRegex(notify.DeliveryError, "three attempts"):
            notify.send_message(self.event, self.config, opener=opener, sleep=sleep)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2])
        self.assertEqual(len(opener.calls), 3)
        for delay in ("30", "-1", "nan", "infinity", "not-a-number"):
            opener = FakeOpener(http_error(429, delay))
            sleep = Mock()
            with self.subTest(delay=delay), self.assertRaises(notify.DeliveryError):
                notify.send_message(self.event, self.config, opener=opener, sleep=sleep)
            sleep.assert_not_called()
            self.assertEqual(len(opener.calls), 1)

    def test_authentication_redirects_and_server_errors_are_not_retried(self):
        for status in (400, 401, 403, 404, 302, 500, 502, 503):
            opener = FakeOpener(http_error(status, body=b'{"secret":"test-only-%key"}'))
            sleep = Mock()
            with (
                self.subTest(status=status),
                self.assertRaises(notify.DeliveryError) as caught,
            ):
                notify.send_message(self.event, self.config, opener=opener, sleep=sleep)
            self.assertNotIn(self.config.key, str(caught.exception))
            self.assertEqual(len(opener.calls), 1)
            sleep.assert_not_called()

    def test_timeout_and_certificate_failure_do_not_blindly_resend(self):
        for error in (
            TimeoutError("private text"),
            urllib.error.URLError("private text"),
            ssl.SSLCertVerificationError("private text"),
        ):
            opener = FakeOpener(error)
            with (
                self.subTest(error=type(error).__name__),
                self.assertRaises(notify.DeliveryError) as caught,
            ):
                notify.send_message(self.event, self.config, opener=opener)
            self.assertEqual(len(opener.calls), 1)
            self.assertNotIn("private text", str(caught.exception))

    def test_invalid_success_responses_are_unknown_delivery_without_retry(self):
        for body in (
            b"not JSON",
            b"[]",
            b'{"result":"error","msg":"private text"}',
            b'{"result":"success","id":true}',
            b'{"result":"success","id":0}',
            b'{"result":"success"}',
            b"x" * (notify.MAX_RESPONSE_BYTES + 1),
        ):
            opener = FakeOpener(Response(body))
            with (
                self.subTest(size=len(body)),
                self.assertRaises(notify.DeliveryError) as caught,
            ):
                notify.send_message(self.event, self.config, opener=opener)
            self.assertEqual(len(opener.calls), 1)
            self.assertNotIn("private text", str(caught.exception))

    def test_default_transport_installs_a_redirect_blocker(self):
        opener = FakeOpener(Response())
        with patch.object(
            notify.urllib.request, "build_opener", return_value=opener
        ) as factory:
            notify.send_message(self.event, self.config)
        handler = factory.call_args.args[0]
        self.assertIsInstance(handler, notify.NoRedirects)
        self.assertIsNone(
            handler.redirect_request(
                None, None, 302, "", {}, "https://elsewhere.invalid"
            )
        )


class CommandTests(unittest.TestCase):
    def test_preview_never_reads_credentials_or_opens_a_connection(self):
        output = io.StringIO()
        with (
            patch.object(
                notify, "read_config", side_effect=AssertionError("credentials read")
            ),
            patch.object(
                notify.urllib.request,
                "build_opener",
                side_effect=AssertionError("network opened"),
            ),
            redirect_stdout(output),
        ):
            status = notify.main(["--event", str(EXAMPLE)])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue())["to"], "development-events")

    def test_approved_channel_is_checked_before_credentials_or_network(self):
        errors = io.StringIO()
        with (
            patch.object(
                notify, "read_config", side_effect=AssertionError("credentials read")
            ),
            redirect_stderr(errors),
        ):
            status = notify.main(
                [
                    "--event",
                    str(EXAMPLE),
                    "--send",
                    "--config",
                    "private-file",
                    "--site",
                    "https://chat.example.invalid",
                    "--channel",
                    "wrong-channel",
                ]
            )
        self.assertEqual(status, 2)
        self.assertIn("approved destination", errors.getvalue())

    def test_success_and_delivery_failure_have_distinct_exit_codes(self):
        args = [
            "--event",
            str(EXAMPLE),
            "--send",
            "--config",
            "private-file",
            "--site",
            "https://chat.example.invalid",
            "--channel",
            "development-events",
        ]
        config = notify.BotConfig(
            "https://chat.example.invalid", "ci@example.invalid", "test-only"
        )
        for result, expected in ((42, 0), (notify.DeliveryError("HTTP 401"), 1)):
            output, errors = io.StringIO(), io.StringIO()
            with (
                patch.object(notify, "read_config", return_value=config),
                patch.object(
                    notify,
                    "send_message",
                    **(
                        {"side_effect": result}
                        if isinstance(result, Exception)
                        else {"return_value": result}
                    ),
                ),
                redirect_stdout(output),
                redirect_stderr(errors),
            ):
                self.assertEqual(notify.main(args), expected)
            self.assertNotIn("test-only", output.getvalue() + errors.getvalue())

    def test_preview_runs_from_another_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--event", str(EXAMPLE)],
                cwd=directory,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["topic"], "CI / Repository checks")


if __name__ == "__main__":
    unittest.main()
