# Changelog

## 0.26.0 — 2026-07-08

### Added

- **Split-brain detection — duplicate primaries in a shard** (#305, valkey#2261).
  Topology-level detector flags a hash-slot range claimed by more than one
  `master`-flagged node and names the phantom primary (the one with the lower
  `configEpoch`). Emits a `CRITICAL` `CLUSTER_TOPOLOGY` anomaly, deduped per
  conflict signature and re-armed once the conflict resolves.
- **Stalled BGSAVE / AOF persistence-fork detection** (#294, valkey#2322).
  State-based detector tracks RDB and AOF fork children from `INFO persistence`
  and fires when progress freezes (`MONITOR_PERSISTENCE_STALL_SEC`, default 60s),
  elapsed time exceeds a ceiling (`MONITOR_PERSISTENCE_CRIT_SEC`, default 600s),
  or last-save/last-rewrite status flips `ok → err`; WARNING while still
  advancing past `MONITOR_PERSISTENCE_WARN_SEC` (default 120s). Fires once per
  episode and clears when the child exits.
- **Data-loss guard for empty-primary full resync** (#302, valkey#579, Pro).
  Detects the silent data-loss scenario where a persistence-less primary
  restarts empty and replicas full-resync onto the empty dataset. Rule A alerts
  when the primary returns empty with restart evidence (replid change / uptime
  reset / offset regression); Rule B confirms a replica whose keyspace collapsed
  ≥90% after a replid change. Same-replid `FLUSHALL` is deliberately not flagged.
  Adds the Pro-tier `data.loss.detected` webhook and a remediation banner on the
  Anomaly dashboard.
- **P99 latency regression guard for version upgrades** (#304, valkey#3527, Pro).
  Uses `INFO latencystats` to open a 24h window on a version change; when an
  eligible command's P99 stays ≥1.5× its pre-upgrade baseline (and ≥1ms above
  it) for 5 consecutive samples, fires one aggregated `command_p99` anomaly and
  dispatches the Pro-tier `latency.regression.detected` webhook with a runbook.
  Adds a `latencystats` poller (60s / 7d retention), the
  `latency_stats_samples` store across all adapters, and
  `GET /metrics/latencystats/summary` + `/history` (Community).
- **Bulk delete-by-pattern (client-side SCANDEL)** (#308, valkey#2623, Pro).
  Client-driven `SCAN` + per-key `UNLINK` walk with dry-run preview, `maxKeys`
  cap with truncation reporting, inter-batch pacing, cooperative cancel, and
  cluster fan-out (per-key `UNLINK` avoids `CROSSSLOT`). Catch-all `*` requires
  explicit confirmation. Gated behind the new `bulkDelete` feature and a required
  connection header.

### Changed

- **Adaptive webhook retry polling** (#157). `WebhookProcessorService` replaces
  the fixed 10s `setInterval` with a self-scheduling `setTimeout` loop: 2s while
  retries are pending, 10s when the queue is idle (unchanged DB load), with a
  clean shutdown guard. Backoff retries (1s/2s/4s) are now picked up in ~2s
  instead of waiting up to 10s.
- **Centralized `ENV_DEFAULT_ID`** (#156). Replaces 28+ hardcoded
  `'env-default'` string literals across DTOs, tests, and seed scripts with a
  single constant. SQL schema defaults are intentionally left as literals.

### Fixed

- **MCP `info` endpoint** (#280) now passes the `section` parameter through to
  the underlying INFO call.

## 0.25.0

### Added

- **MONITOR capture sessions** — on-demand command capture for
  Valkey / Redis instances with a live tail, post-capture filters,
  JSON / CSV export, four-axis cross-reference against connection
  history, and a pre-flight modal that surfaces provider warnings,
  ACL gaps (with copy-to-clipboard `ACL SETUSER` snippet), health
  signals, and a throughput estimate. Cluster fan-out captures one
  primary at a time or all primaries in parallel into a single
  logical session. Pro+: anomaly-triggered captures from
  `/anomalies`, scheduled captures (interval picker by default,
  `Advanced` cron field), capture-vs-capture diff. Webhooks for
  every lifecycle transition (`monitor.session.started` /
  `completed` / `truncated` / `skipped`, `monitor.trigger.created`).
  Server-side `MONITOR_REDACT_VALUES` toggle scrubs write-command
  payloads at the source. Data retention follows the existing
  tier-based sweep (community 7 d, Pro 90 d, enterprise 365 d).
  See [`docs/monitor.md`](docs/monitor.md).

### Removed

- The `MONITOR_DEV_PREVIEW` / `VITE_MONITOR_DEV_PREVIEW` gates that
  hid the MONITOR routes and UI during the staged rollout. The
  feature is now always available; license tier and the existing
  demo-mode guard are the only gates.
