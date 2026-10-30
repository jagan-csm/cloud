import os
from flask import Flask, jsonify
from common.telemetry import setup_telemetry
from common.faults import fault_blueprint, apply_fault
app = Flask(__name__)
log = setup_telemetry(app, "product-service")
app.register_blueprint(fault_blueprint)

@app.get("/health")
def health():
    return jsonify(service="product-service", status="healthy")

@app.get("/products/<product_id>")
def product(product_id):
    fault = apply_fault()
    if fault:
        body, code = fault
        return jsonify(body), code
    return jsonify(product_id=product_id, name="Demo Product", in_stock=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8001")))
