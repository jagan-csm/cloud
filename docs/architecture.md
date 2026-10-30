# Architecture

```mermaid
flowchart TD
  U[Browser] --> D[Flask Dashboard :5000]
  D --> G[API Gateway :8000]
  G --> O[Order Service :8002]
  O --> P[Product Service :8001]
  O --> PAY[Payment Service :8003]
  G --> M[Prometheus metrics]
  O --> M
  P --> M
  PAY --> M
  G --> L[JSONL logs]
  O --> L
  P --> L
  PAY --> L
  L --> PT[Promtail] --> LO[Loki]
  G -. OpenTelemetry OTLP .-> J[Jaeger]
  O -. OpenTelemetry OTLP .-> J
  P -. OpenTelemetry OTLP .-> J
  PAY -. OpenTelemetry OTLP .-> J
  M --> GR[Grafana]
  LO --> GR
```

Metrics answer what is changing, logs describe specific events, and traces show the path and duration of a request across services. The incident workflow uses a metric to spot an issue, a trace to narrow the slow operation, and logs to inspect relevant errors.
