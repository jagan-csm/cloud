import requests
for name, url in [
    ("dashboard", "http://localhost:5000/health"),
    ("gateway", "http://localhost:8000/health"),
    ("product", "http://localhost:8001/health"),
    ("order", "http://localhost:8002/health"),
    ("payment", "http://localhost:8003/health"),
]:
    try:
        r = requests.get(url, timeout=2)
        print(f"{name}: HTTP {r.status_code} {r.text}")
    except requests.RequestException as exc:
        print(f"{name}: UNREACHABLE ({exc})")
