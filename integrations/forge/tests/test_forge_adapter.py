"""Read-only provider adapter behavior; all HTTP is mocked."""

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import forge_adapter as adapter  # noqa: E402

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
REPO = "example/openops-platform"


class Response(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class AdapterTests(unittest.TestCase):
    def payload(self, provider):
        return json.loads((FIXTURES / f"{provider}-pr.json").read_text())

    def event(self, provider):
        number, site = (
            (17, None)
            if provider == "github"
            else (31, "https://forge.example.invalid")
        )
        return adapter.normalize(
            provider, REPO, number, self.payload(provider), site=site
        )

    def test_github_expected_snapshot(self):
        expected = json.loads((FIXTURES / "expected-github.json").read_text())
        self.assertEqual(self.event("github"), expected)

    def test_forgejo_expected_snapshot(self):
        expected = json.loads((FIXTURES / "expected-forgejo.json").read_text())
        self.assertEqual(self.event("forgejo"), expected)

    def test_distinct_provider_identity_but_same_change(self):
        gh, fj = self.event("github"), self.event("forgejo")
        self.assertNotEqual(gh["id"], fj["id"])
        self.assertEqual(gh["data"]["logical_change"], fj["data"]["logical_change"])
        self.assertEqual(gh["data"]["revision"], fj["data"]["revision"])
        self.assertEqual(gh, self.event("github"))

    def test_merged_differs_from_open(self):
        p = self.payload("github")
        p.update(state="closed", merged_at="2026-11-20T00:00:00Z")
        merged = adapter.normalize("github", REPO, 17, p)
        self.assertEqual(merged["data"]["state"], "merged")
        self.assertNotEqual(merged["id"], self.event("github")["id"])

    def test_reject_invalid_input(self):
        base = self.payload("github")
        edits = (
            ("number", 18),
            ("number", True),
            ("state", "queued"),
            ("html_url", "http://example.invalid"),
            ("merged_at", 12),
            ("merged_at", "2026-11-20T00:00:00Z"),
            ("head", {}),
            ("head", {"sha": "short"}),
        )
        for key, value in edits:
            p = copy.deepcopy(base)
            p[key] = value
            with (
                self.subTest(key=key, value=value),
                self.assertRaises(adapter.ForgeError),
            ):
                adapter.normalize("github", REPO, 17, p)
        for repo in ("../bad", "a/b/c", "a b/repo"):
            with self.subTest(repo=repo), self.assertRaises(adapter.ForgeError):
                adapter.normalize("github", repo, 17, base)
        for number in (0, -1, True, "17"):
            with self.subTest(number=number), self.assertRaises(adapter.ForgeError):
                adapter.normalize("github", REPO, number, base)
        with self.assertRaises(adapter.ForgeError):
            adapter.normalize("other", REPO, 17, base)

    def test_reject_unsafe_origins(self):
        bad_sites = (
            "http://forge.example.invalid",
            "https://user:pass@forge.example.invalid",
            "https://forge.example.invalid/a",
            "https://forge.example.invalid/?x=1",
            "https://forge.example.invalid:bad",
            42,
        )
        for site in bad_sites:
            with self.subTest(site=site), self.assertRaises(adapter.ForgeError):
                adapter.normalize(
                    "forgejo", REPO, 31, self.payload("forgejo"), site=site
                )

    def test_api_requests_are_only_get(self):
        cases = (
            (
                "github",
                17,
                None,
                "https://api.github.com/repos/example/openops-platform/pulls/17",
            ),
            (
                "forgejo",
                31,
                "https://forge.example.invalid",
                "https://forge.example.invalid/api/v1/repos/"
                "example/openops-platform/pulls/31",
            ),
        )
        for provider, number, site, expected in cases:
            fake = Mock()
            data = json.dumps(self.payload(provider)).encode()
            fake.open.side_effect = lambda req, timeout: Response(data)
            result = adapter.fetch_pull_request(
                provider, REPO, number, site=site, opener=fake
            )
            args, kwargs = fake.open.call_args
            self.assertEqual(args[0].get_method(), "GET")
            self.assertEqual(args[0].full_url, expected)
            self.assertEqual(kwargs["timeout"], 5)
            self.assertEqual(result["data"]["provider"], provider)

    def test_http_failures_do_not_pass_as_success(self):
        fake = Mock()
        cases = (
            urllib.error.HTTPError(
                "https://example.invalid", 403, "forbidden", {}, io.BytesIO(b"private")
            ),
            urllib.error.HTTPError(
                "https://example.invalid", 500, "oops", {}, io.BytesIO(b"private")
            ),
            urllib.error.URLError("offline"),
            TimeoutError(),
        )
        for failure in cases:
            fake.open.side_effect = failure
            with (
                self.subTest(failure=type(failure).__name__),
                self.assertRaises(adapter.ForgeError) as raised,
            ):
                adapter.fetch_pull_request("github", REPO, 17, opener=fake)
            self.assertNotIn("private", str(raised.exception))

    def test_invalid_http_payloads(self):
        fake = Mock()
        invalid = (b"{invalid", b'{"number":1,"number":2}', b"[]", b"\xff")
        for body in (*invalid, b"a" * 65_537):
            fake.open.side_effect = lambda req, timeout, data=body: Response(data)
            with self.subTest(size=len(body)), self.assertRaises(adapter.ForgeError):
                adapter.fetch_pull_request("github", REPO, 17, opener=fake)

        class BadStatus(Response):
            status = 302

        fake.open.side_effect = lambda req, timeout: BadStatus(b"{}")
        with self.assertRaises(adapter.ForgeError):
            adapter.fetch_pull_request("github", REPO, 17, opener=fake)


class PreviewTests(unittest.TestCase):
    def test_cli_fixture(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = adapter.main(
                [
                    "--provider",
                    "github",
                    "--repository",
                    REPO,
                    "--number",
                    "17",
                    "--fixture",
                    str(FIXTURES / "github-pr.json"),
                ]
            )
        self.assertEqual(status, 0)
        expected = json.loads((FIXTURES / "expected-github.json").read_text())
        self.assertEqual(json.loads(output.getvalue()), expected)

    def test_cli_rejects_bad_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "invalid.json"
            p.write_text('{"number": 17, "number": 17}')
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                status = adapter.main(
                    [
                        "--provider",
                        "github",
                        "--repository",
                        REPO,
                        "--number",
                        "17",
                        "--fixture",
                        str(p),
                    ]
                )
            self.assertEqual(status, 2)
            self.assertIn("duplicate JSON field", output.getvalue())


if __name__ == "__main__":
    unittest.main()
