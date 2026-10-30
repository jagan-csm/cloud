# Cloud Observability, Logging and Distributed Tracing System

A student mini-project demonstrating observability for a small distributed e-commerce workflow. It combines service metrics, structured logs, OpenTelemetry traces, Prometheus, Grafana, Jaeger, Loki/Promtail, alerts, and controlled local fault injection.

## Important scope note

This is a student demonstration build. Fault scenarios are simulated. Dashboard summary counters are in-memory demo counters and are not the same as Prometheus's service-level time series. Prometheus/Grafana provide collected service metrics. CPU/memory process metrics describe each container; node-exporter in Docker Desktop describes the Docker Linux VM, not Windows host metrics.

## Architecture

Browser → Flask dashboard → API Gateway → Order Service → Product Service and Payment Service.

Prometheus scrapes each service's `/metrics`. OpenTelemetry instruments Flask and outbound `requests` calls and exports spans via OTLP/HTTP to Jaeger. Services write JSONL logs to a shared volume; Promtail ships them to Loki.

## Requirements

- Python 3.11 recommended for local mode
- Docker Desktop with Docker Compose for full observability stack
- VS Code (optional)

## Run with Docker

From this directory:

```powershell
docker compose up --build -d
docker compose ps
```

Open:
- Dashboard: http://localhost:5000
- Grafana: http://localhost:3000 (demo credentials `admin` / `admin`)
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093
- Jaeger: http://localhost:16686
- Loki readiness: http://localhost:3100/ready

Use the Dashboard → Demo Controls to generate normal traffic and controlled faults. Give Prometheus a few scrape intervals to populate graphs. Jaeger traces appear after requests complete and OTLP export succeeds.

Stop:
```powershell
docker compose down
```
Stop and remove stored volumes:
```powershell
docker compose down -v
```
The second command deletes persisted demo data.

## Local Python mode

Create a virtual environment and install dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For local mode, start each service in a separate terminal from the project root. Set service URLs to `http://localhost:<port>` and set `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318` if Jaeger is running. Start product (8001), payment (8003), order (8002), gateway (8000), then dashboard (5000). Example:

```powershell
$env:ENABLE_FAULTS="true"; $env:PRODUCT_URL="http://localhost:8001"; python -m services.product_service.main
```

Use separate terminals for each service, adjusting the module and port/environment variables. For the dashboard:
```powershell
$env:PUBLIC_GATEWAY_URL="http://localhost:8000"; python -m app.main
```

If running without Jaeger, the app should still work, but traces will not be exported to a backend.

## Tests

```powershell
pytest -q
```

These are basic dashboard/API tests. They do not replace full Docker integration tests.

## Demonstration

1. Open the dashboard.
2. Click **Generate normal traffic**.
3. Review dashboard counters, service health, and logs.
4. Click **Payment timeout** and inspect the order result/logs.
5. Open Jaeger and search for `order-service` or `api-gateway`.
6. Open Grafana and inspect request rate, error rate, latency, and memory.
7. Click **Recover / reset**.

## APIs

- `GET /api/health`
- `GET /api/metrics/summary`
- `GET /api/alerts`
- `GET /api/incidents`
- `GET /api/logs?q=&level=`
- `POST /api/demo/normal-traffic`
- `POST /api/demo/high-latency`
- `POST /api/demo/payment-timeout`
- `POST /api/demo/application-error`
- `POST /api/demo/service-unavailable`
- `POST /api/demo/recover`

Service endpoints include `/health`, `/metrics`, and `POST /_admin/fault`. Fault injection must be enabled using `ENABLE_FAULTS=true`; it is intended only for local demos.

## Known limitations

- This is a local educational implementation, not a hardened production system.
- Alertmanager rules are configured, but the dashboard's alert table uses a simple application-level evaluator over its own demo request counters. Prometheus alerts are visible in Prometheus/Alertmanager.
- The log viewer reads local JSONL files; Grafana's Loki datasource is provisioned for querying Loki separately.
- The dashboard's in-memory summary counters reset when the dashboard restarts.
- Distributed traces require Jaeger to be reachable at the configured OTLP endpoint.
- A full integration run must be performed on the target machine. No tests should be considered passed until executed there.

## Official documentation

- Flask: https://flask.palletsprojects.com/
- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/grafana/latest/
- OpenTelemetry Python: https://opentelemetry.io/docs/languages/python/
- Jaeger: https://www.jaegertracing.io/docs/
- Loki: https://grafana.com/docs/loki/latest/
- Docker Compose: https://docs.docker.com/compose/
