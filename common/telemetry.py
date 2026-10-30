import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from flask import Response, request, g
from common.jsonlog import configure_logging

REQUESTS = Counter("http_requests_total", "HTTP requests", ["service", "method", "endpoint", "status"])
LATENCY = Histogram("http_request_duration_seconds", "HTTP request duration", ["service", "endpoint"])
CPU = Gauge("process_cpu_percent", "Process CPU percent", ["service"])
MEMORY = Gauge("process_memory_bytes", "Process memory bytes", ["service"])
ORDERS = Counter("orders_total", "Orders processed", ["result"])
PAYMENT_FAILURES = Counter("payment_failures_total", "Payment failures")

def setup_telemetry(app, service_name):
    logger = configure_logging(service_name)
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318").rstrip("/")
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        trace.set_tracer_provider(provider)
        try:
            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")))
        except Exception as exc:
            logger.warning("OTLP exporter setup failed: %s", exc)
    try:
        FlaskInstrumentor().instrument_app(app)
    except Exception:
        pass
    try:
        RequestsInstrumentor().instrument()
    except Exception:
        pass

    @app.before_request
    def _start_timer():
        import time
        g._obs_start = time.perf_counter()

    @app.after_request
    def _record(response):
        import time
        elapsed = time.perf_counter() - getattr(g, "_obs_start", time.perf_counter())
        endpoint_name = request.url_rule.rule if request.url_rule else request.path
        REQUESTS.labels(service_name, request.method, endpoint_name, str(response.status_code)).inc()
        LATENCY.labels(service_name, endpoint_name).observe(elapsed)
        try:
            import psutil
            CPU.labels(service_name).set(psutil.Process().cpu_percent(interval=None))
            MEMORY.labels(service_name).set(psutil.Process().memory_info().rss)
        except Exception:
            pass
        return response

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    return logger
