# ChatOps files

Paths are relative to the repository root.

| Path | Purpose |
| --- | --- |
| `scripts/notifications/notify_zulip.py` | Existing v1 parser, preview and explicit-send transport |
| `scripts/notifications/preview_route.py` | Proposed provider/repository/PR topic; preview only |
| `tests/notifications/test_notify_zulip.py` | Notifier behavior and transport failures |
| `tests/notifications/test_preview_route.py` | Routing isolation, recovery grouping and invalid-input cases |
| `examples/notifications/*-failure.json` | Existing synthetic v1 events for both providers |
| `docs/ci/zulip-notifications.md` | Notifier contract and operator instructions |
| `integrations/chatops/Makefile` | Scoped offline checks and routing preview |
| `integrations/chatops/README.md` | Proposed routing behavior and coordination limits |
| `integrations/chatops/docs/CHECKS.md` | Commands, expected results and failure recovery |

The separate Gotify lane owns `integrations/chatops/gotify/`. Its adapter is not
required by this component's checks. No existing path is moved.
