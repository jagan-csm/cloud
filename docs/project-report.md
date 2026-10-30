# Cloud Observability, Logging and Distributed Tracing System

## Abstract
This project demonstrates a local observability framework for a distributed web application. It collects service metrics, structured logs, and distributed traces to help investigate latency and errors.

## Problem statement
When a request passes through multiple services, checking each service separately makes it difficult to find where latency or failures begin. The project provides a shared dashboard and connected observability tools to support systematic investigation.

## Objectives
- Collect application metrics with Prometheus.
- Visualize metrics with Grafana.
- Generate structured service logs and collect them centrally.
- Trace HTTP requests across services using OpenTelemetry and Jaeger.
- Demonstrate alerts and incident investigation with controlled faults.

## Proposed system
A Flask dashboard sends requests through an API Gateway to Order, Product, and Payment services. Prometheus scrapes metrics, OpenTelemetry exports traces to Jaeger, and Promtail sends JSONL logs to Loki. A SQLite database stores incident history.

## Modules
1. Dashboard and API
2. API Gateway
3. Product Service
4. Order Service
5. Payment Service
6. Metrics collection
7. Structured logging
8. Distributed tracing
9. Alerts and incident history
10. Controlled fault demonstration

## Testing
Basic tests are supplied for dashboard rendering and API behavior. Full integration validation requires running the stack with Docker Compose and checking Prometheus, Grafana, Jaeger, and Loki.

## Limitations
This is an educational local prototype. It is not hardened for production. Some dashboard summaries are in-memory demonstration counters, and service metrics must be interpreted separately from those counters. Simulated faults are not real infrastructure failures.

## Future scope
Possible improvements include authentication, role-based access, cloud deployment, Kubernetes monitoring, richer log-to-trace correlation, and more robust incident detection.
