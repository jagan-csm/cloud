import os
from flask import Flask
from app.routes import bp
from common.telemetry import setup_telemetry

def create_app():
    app = Flask(__name__)
    setup_telemetry(app, "observability-dashboard")
    app.register_blueprint(bp)
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)