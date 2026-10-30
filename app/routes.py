import os, json, glob, requests
from flask import Blueprint, jsonify, render_template, request
from prometheus_client.parser import text_string_to_metric_families
from app.config import SERVICE_URLS
from app.incidents import init_db, list_incidents, create_incident, resolve_incidents
from app.alerts import evaluate_alerts
from app.explain import explain_incident

bp = Blueprint("main", __name__)
init_db()
memory = {"requests": 0, "errors": 0, "latency_samples": [], "demo_events": []}

@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/api/health")
def api_health():
    results = {}
    for name, base in SERVICE_URLS.items():
        try:
            r = requests.get(base + "/health", timeout=1.2)
            results[name] = {"status": "healthy" if r.ok else "unhealthy", "http_status": r.status_code}
        except requests.RequestException:
            results[name] = {"status": "unreachable", "http_status": None}
    return jsonify(results)

@bp.get("/api/metrics/summary")
def metrics_summary():
    n = memory["requests"]
    errors = memory["errors"]
    lat = memory["latency_samples"]
    snapshot = {"total_requests": n, "failed_requests": errors, "success_requests": n-errors,
        "error_rate": errors/n if n else 0, "avg_latency_ms": sum(lat)/len(lat) if lat else 0,
        "active_services": None, "source": "dashboard demo request counters; Prometheus is configured separately"}
    return jsonify(snapshot)

@bp.get("/api/alerts")
def alerts():
    return jsonify(evaluate_alerts({"error_rate": memory["errors"]/memory["requests"] if memory["requests"] else 0,
        "avg_latency_ms": sum(memory["latency_samples"])/len(memory["latency_samples"]) if memory["latency_samples"] else 0}))

@bp.get("/api/incidents")
def incidents():
    return jsonify(list_incidents())

@bp.get("/api/logs")
def logs():
    service = request.args.get("service", "")
    level = request.args.get("level", "").upper()
    query = request.args.get("q", "").lower()
    log_dir = os.getenv("LOG_DIR", "/var/log/obs")
    paths = glob.glob(os.path.join(log_dir, "*.jsonl")) + glob.glob(os.path.join("logs", "*.jsonl"))
    rows = []
    for path in set(paths):
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    try: item = json.loads(line)
                    except json.JSONDecodeError: continue
                    if service and service not in item.get("service", ""): continue
                    if level and item.get("level", "").upper() != level: continue
                    if query and query not in json.dumps(item).lower(): continue
                    rows.append(item)
        except OSError:
            continue
    rows.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return jsonify(rows[-300:][::-1])

@bp.post("/api/demo/<scenario>")
def demo(scenario):
    mapping = {
        "normal-traffic": ("normal", "normal", "normal"),
        "high-latency": ("normal", "normal", "delay"),
        "payment-timeout": ("normal", "normal", "timeout"),
        "application-error": ("normal", "normal", "error"),
        "service-unavailable": ("normal", "normal", "unavailable"),
    }
    if scenario == "recover":
        modes = {name: "normal" for name in SERVICE_URLS}
        resolve_incidents()
    elif scenario in mapping:
        gw, order, payment = mapping[scenario]
        modes = {"API Gateway": gw, "Order Service": order, "Payment Service": payment, "Product Service": "normal"}
    else:
        return jsonify(error="Unknown scenario"), 404

    for name, mode in modes.items():
        base = SERVICE_URLS.get(name)
        if not base: continue
        try:
            requests.post(base + "/_admin/fault", json={"mode": mode, "delay_seconds": 4 if mode == "timeout" else 2}, timeout=1)
        except requests.RequestException:
            pass
    result = {"scenario": scenario, "simulated": True, "fault_modes": modes}
    if scenario == "normal-traffic":
        for _ in range(3):
            _send_order()
    elif scenario != "recover":
        _send_order()
    return jsonify(result)

def _send_order():
    import time
    import requests as rq
    import os
    url = os.getenv("PUBLIC_GATEWAY_URL", "http://localhost:8000") + "/api/orders"
    start = time.perf_counter()
    memory["requests"] += 1
    try:
        r = rq.post(url, json={"product_id": "demo-product"}, timeout=7)
        if not r.ok: memory["errors"] += 1
        return r.status_code
    except rq.RequestException:
        memory["errors"] += 1
        return 0
    finally:
        memory["latency_samples"].append((time.perf_counter()-start)*1000)
        memory["latency_samples"] = memory["latency_samples"][-200:]
