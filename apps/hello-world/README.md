# Hello World fixture

One anime-themed HTML page. No application code, JavaScript, API, database or
external assets. The container serves only `public/`.

The other files are test material for OpenOps. They are not used by the page.
Nothing in this directory publishes an image or deploys to a cluster.

## Start here

From this directory:

```sh
make check
make run
```

In another terminal:

```sh
make smoke
```

`make run` uses Python's development-only static server on port 8080. Stop it
with Ctrl+C. The container uses unprivileged NGINX instead.

## Where to look

| Need | File |
| --- | --- |
| Change the banner | `public/index.html`, `public/style.css` |
| Check sample data | `fixtures/` and `scripts/verify.py` |
| See what's tested | `tests/`, `docs/CHECKS.md` |
| Find out why a file exists | `docs/FILES.md` |
| Run a check | `Makefile` |
| Try a container later | `Dockerfile`, `compose.yaml` |

## Rules

- `make check` uses Python's standard library and POSIX shell. It needs no
  Docker daemon, account, network or cluster.
- Docker and Compose commands are manual, not part of `make check`.
- CSV, TSV, XML and other specimens describe the same invented episode.
  Changing one without changing the others is supposed to fail.
- SQL, metrics, HTTP, RSS, log and config examples are checked offline.
  None is read by the web page.
- The Python scripts are test and tooling code, not application services.
- Root CI, root Makefile, registry and platform deployment are unchanged.

Use `make prose-check` in the full OpenOps checkout for the vendored
SlopMonster review; it is opt-in until the platform adopts this workload.

See [check commands](docs/CHECKS.md) before adding a new format.
