import os, time
from flask import Blueprint, request, jsonify

faults = {"mode": "normal", "delay_seconds": 0}
fault_blueprint = Blueprint("faults", __name__)

@fault_blueprint.post("/_admin/fault")
def set_fault():
    if os.getenv("ENABLE_FAULTS", "false").lower() != "true":
        return jsonify({"error": "Fault injection disabled"}), 403
    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "normal")
    if mode not in {"normal", "delay", "error", "unavailable", "timeout"}:
        return jsonify({"error": "Unsupported mode"}), 400
    try:
        delay = float(data.get("delay_seconds", 2 if mode in {"delay", "timeout"} else 0))
    except (TypeError, ValueError):
        return jsonify({"error": "delay_seconds must be numeric"}), 400
    faults.update(mode=mode, delay_seconds=max(0, min(delay, 10)))
    return jsonify({"mode": faults["mode"], "delay_seconds": faults["delay_seconds"], "simulated": True})

def apply_fault():
    mode = faults["mode"]
    if mode in {"delay", "timeout"}:
        time.sleep(faults["delay_seconds"])
    if mode == "error":
        return {"error": "Simulated service error", "simulated": True}, 500
    if mode == "unavailable":
        return {"error": "Simulated service unavailable", "simulated": True}, 503
    return None
