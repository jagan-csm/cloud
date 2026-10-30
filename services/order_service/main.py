import os, uuid, requests
from flask import Flask, jsonify, request
from common.telemetry import setup_telemetry, ORDERS
from common.faults import fault_blueprint, apply_fault
app = Flask(__name__)
log = setup_telemetry(app, "order-service")
app.register_blueprint(fault_blueprint)
PRODUCT_URL = os.getenv("PRODUCT_URL", "http://localhost:8001")
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://localhost:8003")

@app.get("/health")
def health():
    return jsonify(service="order-service", status="healthy")

@app.post("/orders")
def create_order():
    fault = apply_fault()
    if fault:
        body, code = fault
        if code >= 500: ORDERS.labels("failed").inc()
        return jsonify(body), code
    data = request.get_json(silent=True) or {}
    product_id = str(data.get("product_id", "demo-product"))
    order_id = str(uuid.uuid4())[:8]
    try:
        p = requests.get(f"{PRODUCT_URL}/products/{product_id}", timeout=3)
        p.raise_for_status()
        payment = requests.post(f"{PAYMENT_URL}/charge", json={"order_id": order_id}, timeout=2)
        payment.raise_for_status()
        ORDERS.labels("success").inc()
        log.info("Order completed order_id=%s", order_id)
        return jsonify(order_id=order_id, status="confirmed", product=p.json(), payment=payment.json()), 201
    except requests.Timeout:
        ORDERS.labels("failed").inc()
        log.exception("Downstream service timeout order_id=%s", order_id)
        return jsonify(error="Downstream service timed out", order_id=order_id), 504
    except requests.RequestException as exc:
        ORDERS.labels("failed").inc()
        log.error("Order failed order_id=%s reason=%s", order_id, str(exc))
        return jsonify(error="Order could not be completed", order_id=order_id), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8002")))
