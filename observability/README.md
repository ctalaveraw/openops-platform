# Observability

Offline exercises for monitoring one static HTTP workload. The rule consumes
synthetic Blackbox Exporter-style probe samples. No exporter is configured.
No application code changes are needed.

From the repository root:

```sh
make -C observability help
make -C observability check
```

Install the Prometheus CLI tools first. See [checks](docs/CHECKS.md) for the
proposed version and failure handling. The component is not wired into root
Make or CI. No monitor, receiver or service is started.

The [file map](docs/FILES.md) lists the specimens. The [runbook](docs/RUNBOOK.md)
describes what a future operator would investigate.
