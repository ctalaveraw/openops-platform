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
`check` uses local Python and shell tools. It does not start a container or
contact the network.

## What the parent may do later

A future root Makefile could call this child with:

```makefile
.PHONY: check-hello
check-hello:
	$(MAKE) -C apps/hello-world check
```

**That rule has not been added.** The root Makefile still checks the platform.
Its CI may discover source files in this folder, but it does not call the child
`check` target. Make passes a failing child exit status back to its caller.

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
errors, inspect `fixtures/`; for banner errors, inspect `public/`. Avoid editing
the parent workflow to bypass a failed child test.
