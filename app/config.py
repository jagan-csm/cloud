import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data", "incidents.db"))
SERVICE_URLS = {
    "API Gateway": os.getenv("PUBLIC_GATEWAY_URL", "http://localhost:8000"),
    "Product Service": os.getenv("PUBLIC_PRODUCT_URL", "http://localhost:8001"),
    "Order Service": os.getenv("PUBLIC_ORDER_URL", "http://localhost:8002"),
    "Payment Service": os.getenv("PUBLIC_PAYMENT_URL", "http://localhost:8003"),
}
