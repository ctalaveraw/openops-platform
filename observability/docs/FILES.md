# Files

| Path | Purpose |
| --- | --- |
| `Makefile` | Independent offline checks. |
| `prometheus.yml` | Rule-loading example without scrape targets. |
| `rules/availability.yml` | Recording rule and one delayed alert. |
| `tests/availability.yml` | Synthetic rule evaluations. |
| `tests/test_alert_samples.py` | Correlation assertions and a negative case. |
| `fixtures/alert-firing.json` | Example Alertmanager webhook. |
| `fixtures/alert-resolved.json` | Matching resolved webhook. |
| `docs/RUNBOOK.md` | Proposed diagnosis and SLO. |
| `docs/EVENTS.md` | Event mapping proposal for lanes 09 and 08. |
| `docs/CHECKS.md` | Tool setup and expected results. |

All fixtures are synthetic. None is scraped or sent by the app.
