import os
os.environ.setdefault("DATABASE_PATH", "/tmp/cloud-observability-test.db")
from app.main import create_app

def test_dashboard_returns_html():
    client = create_app().test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Cloud Observability Dashboard" in response.data

def test_summary_shape():
    client = create_app().test_client()
    response = client.get("/api/metrics/summary")
    assert response.status_code == 200
    data = response.get_json()
    assert "total_requests" in data
    assert "error_rate" in data

def test_unknown_demo_scenario():
    client = create_app().test_client()
    response = client.post("/api/demo/not-a-real-scenario")
    assert response.status_code == 404
