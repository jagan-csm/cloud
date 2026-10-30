import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from opentelemetry import trace

LOG_DIR = Path(os.getenv("LOG_DIR", "/var/log/obs"))
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(parents=True, exist_ok=True)

class JsonLineFormatter(logging.Formatter):
    def format(self, record):
        span = trace.get_current_span()
        ctx = span.get_span_context() if span else None
        trace_id = format(ctx.trace_id, "032x") if ctx and ctx.is_valid else None
        span_id = format(ctx.span_id, "016x") if ctx and ctx.is_valid else None
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", os.getenv("SERVICE_NAME", "dashboard")),
            "message": record.getMessage(),
            "trace_id": trace_id,
            "span_id": span_id,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def configure_logging(service_name):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if logger.handlers:
        logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLineFormatter())
    logger.addHandler(handler)
    try:
        file_handler = logging.FileHandler(LOG_DIR / f"{service_name}.jsonl")
        file_handler.setFormatter(JsonLineFormatter())
        logger.addHandler(file_handler)
    except OSError:
        pass
    logging.LoggerAdapter(logger, {"service": service_name})
    return logging.LoggerAdapter(logger, {"service": service_name})
