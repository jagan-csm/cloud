import time
from app.incidents import create_incident

_last = {}
def evaluate_alerts(snapshot, cooldown_seconds=60):
    alerts = []
    rules = [
        ("high_error_rate", "API Gateway", snapshot.get("error_rate", 0) > 0.10, "critical", "Error rate exceeds 10%"),
        ("high_latency", "API Gateway", snapshot.get("avg_latency_ms", 0) > 1000, "warning", "Average latency exceeds 1000 ms"),
    ]
    now = time.time()
    for rule, service, triggered, severity, message in rules:
        key = (rule, service)
        if triggered:
            alerts.append({"name": rule, "service": service, "severity": severity, "message": message, "status": "active"})
            if now - _last.get(key, 0) > cooldown_seconds:
                create_incident(service, severity, message, snapshot)
                _last[key] = now
    return alerts
