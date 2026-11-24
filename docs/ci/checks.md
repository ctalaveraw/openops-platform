# Repository checks

## Run locally

Use Git, GNU Make, and uv 0.13.9. From the repository root, run:

```sh
make bootstrap
make check
```

Bootstrap installs the Python version selected by `.python-version`, then syncs
the tools in `uv.lock` into `.venv`.
It also installs JavaScript lint dependencies from `package-lock.json`.
The required checks cover Markdown and YAML.
JSON syntax and notification event examples are checked too.
TOML parsing includes `uv.lock`.
Makefile source and public interfaces are checked too.
Python linting and formatting are also required.
ShellCheck runs when shell scripts are present.
Application HTML and CSS are checked when present.
The gate also validates GitHub Actions workflows.
The root check delegates to the Hello World component's offline tests.
It also runs `make test-ci` for root CI validator tests and
`make check-coordination` for delivery safety and required prose.
Run `make check-delivery-guard` or `make check-required-prose`
to troubleshoot those checks independently.
See [Hello World delivery](../delivery/hello-world.md) for separate image checks.
Run `make lint-prose` for the optional prose review.

## Hosted workflow

`.github/workflows/lint.yml` runs for pull requests and pushes to `main`.
The job uses Ubuntu 24.04 and has a ten-minute timeout.
It checks out the repository and installs uv before calling the same Make targets.
Project setup and check commands live in the repository.

The workflow grants `contents: read`.
Checkout does not persist Git credentials. uv caching is disabled.
A nonzero command exit fails the job.

## External actions

| Action and source | Pinned commit | License | Replacement |
| --- | --- | --- | --- |
| [actions/checkout v7.0.1](https://github.com/actions/checkout/tree/3d3c42e5aac5ba805825da76410c181273ba90b1) | `3d3c42e5aac5ba805825da76410c181273ba90b1` | [MIT](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/LICENSE) | Use the CI provider's checkout step and verify the selected commit. |
| [astral-sh/setup-uv v10.3.3](https://github.com/astral-sh/setup-uv/tree/68559e99cc807c1eb7e9238fd43a15bba460eec2) | `68559e99cc807c1eb7e9238fd43a15bba460eec2` | [MIT](https://github.com/astral-sh/setup-uv/blob/68559e99cc807c1eb7e9238fd43a15bba460eec2/LICENSE) | Install uv 0.13.9 from an official Astral release, then run `make bootstrap`. |

Update owner: repository maintainer `ctalaveraw`.
Review release notes before an update.
Confirm the release commit and license before changing its SHA.
Require a successful hosted run before merging the update.

The action release version identifies the action itself.
The uv executable version is selected by `required-version` in `pyproject.toml`.

## Reproduce a failure

Run `make bootstrap`, then `make check` from the repository root.
Read the failed command's output for the affected file and rule.
Fix the source and rerun the same check before pushing.
