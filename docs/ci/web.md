# HTML and CSS checks

Run `make lint-web`.
The required `make check` gate includes this target.

## Scope

The wrapper selects existing tracked and new nonignored files under `apps/`.
Extensions are `.html` and `.htm`. CSS uses `.css`.
Tracked deletions are skipped.
An empty selection prints `SKIP` and succeeds.

Directories named `vendor` or `node_modules` are excluded.
Intentional negative examples belong under `fixtures/invalid/` inside an app.
That directory and its descendants are excluded from normal scans.

## Rules

HTML-validate uses its recommended and document presets.
Integrity metadata is required for remote assets.
Stylelint uses its recommended error rules with property-value validation.
PostCSS HTML checks style blocks and inline style attributes.
HTML without CSS is allowed.

Sources are read as UTF-8 and checked without rewriting them.
Browser behavior belongs to later runtime tests.

## Tooling and setup

Run `make bootstrap`.
uv installs the third-party `nodejs-wheel==24.19.0` distribution into `.venv`.
That provides Node and npm for these checks.
JavaScript packages are installed in ignored `node_modules/`.

| Lockfile | Purpose |
| --- | --- |
| `uv.lock` | Python packages and the Node distribution. |
| `package-lock.json` | JavaScript linters and their dependencies. |

The Make setup target calls `check_web.py --setup`.
That runs `npm ci` with package lifecycle scripts disabled.
npm's cache lives under `.venv/npm-cache/`.
Update the npm lockfile explicitly when changing `package.json`.

Normal checks inspect installed dependencies offline before selecting source.
Both validators receive explicit root configuration files.
The wrapper derives paths from its location.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | Selected source passed, or the scope was empty. |
| `1` | Source findings were reported. |
| `2` | Setup failed or a tool could not complete. |

These are wrapper statuses. GNU Make reports a failed recipe with its own
nonzero exit status.
