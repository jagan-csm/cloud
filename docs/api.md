# API reference

Dashboard:
- `GET /api/health`: checks configured services.
- `GET /api/metrics/summary`: returns in-memory demonstration request summary.
- `GET /api/alerts`: evaluates dashboard demo thresholds.
- `GET /api/incidents`: lists SQLite incident records.
- `GET /api/logs?q=<text>&level=<level>&service=<service>`: searches readable JSONL log files.
- `POST /api/demo/<scenario>`: triggers a demo scenario; supported values are `normal-traffic`, `high-latency`, `payment-timeout`, `application-error`, `service-unavailable`, `recover`.

Services:
- `GET /health`
- `GET /metrics`
- `POST /_admin/fault` with JSON such as `{"mode":"timeout","delay_seconds":4}` when `ENABLE_FAULTS=true`.
