# Hello World probe runbook

Status: example for review. No live alert or measured SLO exists.

## Signal

An external HTTP probe supplies `probe_success` for the single expected
target. One is success and zero is failure. The recording rule preserves
that value. Missing samples are not counted as success. The warning fires
after two continuous minutes of failure or absent data. Ordinary missed
scrapes may retain recent samples within the Prometheus lookback window.
The test uses an explicit stale marker to exercise loss of the series.

## Investigation

In an authorized environment, inspect the probe result and scrape target.
If the probe reports failure, check DNS and HTTP from the probe vantage point.
If the series is absent, inspect the exporter and scrape configuration.
Compare rollout identity with the reviewed source revision. Preserve evidence
before making a recovery change.

A successful external probe and fresh samples confirm recovery. An empty
alert list on its own is not proof of service health. Keep host-level access
and an independent notification path for monitoring or event fabric outage.

## Proposed availability objective

For #196, evaluate successful HTTP probe intervals against expected intervals
over a seven-day exercise window. Candidate target: 99%. Missing intervals
are unknown and must be reported separately. Do not claim the target was met
while coverage is incomplete. Define maintenance exclusions before measuring.

Record timestamps, observed successes and failures, unknown intervals, and
alert transitions in a later controlled exercise. The synthetic rule tests
are not SLO measurements or an incident report.
