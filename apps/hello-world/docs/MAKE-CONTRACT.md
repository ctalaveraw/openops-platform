# Component Make contract

Each component owns its checks. The platform can call a component's Makefile
without reading its scripts or knowing which language it uses.

## Run the child directly

From the OpenOps repository root:

```sh
make -C apps/hello-world help
make -C apps/hello-world check
```

From this directory, use `make check`. Both forms run the same tasks.

Focused `check-static` and `check-formats` targets accept `CASE`.
They are diagnostic commands, not additions to the required component
interface. The full `check` target runs all required checks.
`check` uses Python, Make, Git and shell tools. It does not start a container or
contact the network.

## Parent delegation

The root Makefile now has a `check-apps` target that calls:

```sh
make -C apps/hello-world check
```

`make check` runs the platform's checks and then the child target.
A failing child exits nonzero and makes the parent check fail.
Neither command builds an image, starts a container or publishes anything.

The same pattern can be considered later for provisioning and host-baseline
components. Each would keep its own Makefile, tests and dependencies. This
fixture defines no rules for those components.

## What is declared

`contracts/component.json` lists four Make targets and the existing runtime
paths. `schemas/component.schema.json` documents the shape. Local tests check
that the declared targets exist and that the HTTP metadata matches the current
workload example. Schema validation is opt-in through `make schema-check`.

The JSON file is **an example contract**, not a platform registry or a
configuration read by a running service. No platform process consumes it today.

## When a check fails

Run `make -C apps/hello-world test` to see which assertion failed. For format
errors, inspect `fixtures/`. For banner errors, inspect `public/`. Avoid editing
the parent workflow to bypass a failed child test.
