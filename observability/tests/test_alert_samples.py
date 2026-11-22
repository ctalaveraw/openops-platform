"""Check correlation of the synthetic Alertmanager samples."""

import copy
import json
import unittest
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def load(status: str) -> dict:
    return json.loads((FIXTURES / f"alert-{status}.json").read_text(encoding="utf-8"))


class AlertSampleTests(unittest.TestCase):
    def assert_pair(self, firing: dict, resolved: dict) -> None:
        a = firing["alerts"][0]
        b = resolved["alerts"][0]
        self.assertEqual((firing["status"], a["status"]), ("firing", "firing"))
        self.assertEqual((resolved["status"], b["status"]), ("resolved", "resolved"))
        self.assertEqual(len(firing["alerts"]), 1)
        self.assertEqual(len(resolved["alerts"]), 1)
        self.assertEqual(a["fingerprint"], b["fingerprint"])
        self.assertEqual(a["startsAt"], b["startsAt"])
        self.assertEqual(a["labels"], b["labels"])
        self.assertEqual(a["annotations"], b["annotations"])
        self.assertEqual(firing["groupKey"], resolved["groupKey"])
        self.assertEqual(firing["externalURL"], resolved["externalURL"])
        self.assertGreater(b["endsAt"], b["startsAt"])
        self.assertEqual(a["labels"]["alertname"], "HelloWorldProbeUnavailable")
        self.assertEqual(a["labels"]["owner"], "observability")
        self.assertEqual(a["labels"]["severity"], "warning")

    def test_firing_and_resolved_pair(self) -> None:
        self.assert_pair(load("firing"), load("resolved"))

    def test_unrelated_resolution_is_rejected(self) -> None:
        firing = load("firing")
        resolved = copy.deepcopy(load("resolved"))
        resolved["alerts"][0]["startsAt"] = "2026-01-01T00:02:00Z"
        with self.assertRaises(AssertionError):
            self.assert_pair(firing, resolved)


if __name__ == "__main__":
    unittest.main()
