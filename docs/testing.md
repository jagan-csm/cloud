# Testing plan

Run unit tests with `pytest -q`. Then run `docker compose up --build -d` and verify:

1. `docker compose ps` shows expected containers.
2. Dashboard and all service `/health` endpoints respond.
3. Prometheus Targets page shows the service targets as UP.
4. Generate normal traffic and confirm request metrics increment.
5. Jaeger shows traces with multiple service spans.
6. Loki is ready and Grafana can query its datasource.
7. Trigger payment timeout and confirm an error response, trace, and log entry.
8. Recover services and verify a normal order succeeds.

Do not mark integration tests passed until actually executed.
