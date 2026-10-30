import os
from flask import Flask, jsonify, request
from common.telemetry import setup_telemetry, PAYMENT_FAILURES
from common.faults import fault_blueprint, apply_fault
app = Flask(__name__)
log = setup_telemetry(app, "payment-service")
app.register_blueprint(fault_blueprint)

@app.get("/health")
def health():
    return jsonify(service="payment-service", status="healthy")

@app.post("/charge")
def charge():
    fault = apply_fault()
    if fault:
        body, code = fault
        if code >= 500:
            PAYMENT_FAILURES.inc()
            log.error("Payment fault injected: %s", body)
        return jsonify(body), code
    data = request.get_json(silent=True) or {}
    log.info("Payment processed for order_id=%s", data.get("order_id"))
    return jsonify(status="paid", transaction_id="demo-txn-001")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8003")))
