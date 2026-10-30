import os, requests
from flask import Flask, jsonify, request
from common.telemetry import setup_telemetry
from common.faults import fault_blueprint, apply_fault
app = Flask(__name__)
log = setup_telemetry(app, "api-gateway")
app.register_blueprint(fault_blueprint)
ORDER_URL = os.getenv("ORDER_URL", "http://localhost:8002")

@app.get("/health")
def health():
    return jsonify(service="api-gateway", status="healthy")

@app.post("/api/orders")
def orders():
    fault = apply_fault()
    if fault:
        body, code = fault
        return jsonify(body), code
    try:
        response = requests.post(f"{ORDER_URL}/orders", json=request.get_json(silent=True) or {}, timeout=5)
        return (response.content, response.status_code, {"Content-Type": "application/json"})
    except requests.Timeout:
        log.exception("Order gateway timeout")
        return jsonify(error="Gateway timeout"), 504
    except requests.RequestException as exc:
        log.error("Order service unavailable: %s", exc)
        return jsonify(error="Order service unavailable"), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
