# Component contract v1

This is the shared Make interface for new components. It does not replace
the existing Hello World workload descriptor or the notifier event format.

## Required targets

Declare all four targets as `.PHONY`. Use `help` as the default.

| Target | Behavior |
| --- | --- |
| `help` | List implemented commands and prerequisites. |
| `lint` | Validate component source and configuration. |
| `test` | Run component-owned behavior tests. |
| `check` | Run lint and tests, plus any required offline validation. |

After tool bootstrap, check must work offline without credentials, services,
container builds, publication or deployment. Use temporary directories for
generated or negative test inputs. Do not silently skip a required tool.
A failed check returns nonzero. Keep setup and live operations separate.

## Joining the root check

From the repository root, run `make -C <component> check`.
In a separate review, the coordinator adds an explicit child call using
`$(MAKE) -C <component> check`. Never invoke the root check from the child.

Submit the owned path, dependency list, positive and negative command results,
and proof that the check has no delivery side effects. Document the component
in its README, a file map when needed, and docs/CHECKS.md. Include the actual
vendored SlopMonster result for relevant prose. Keep local and CI behavior
equivalent on both forges where verified.

The root currently delegates to Hello World. Additional components require
review. A file, empty folder or passing no-op is not an admitted component.

Keep this interface stable. A breaking change needs a new version and a
reviewed migration of existing consumers.
