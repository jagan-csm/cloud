FROM python:3.11-slim
WORKDIR /workspace
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /var/log/obs /workspace/data
EXPOSE 5000 8000 8001 8002 8003
CMD ["python", "-m", "app.main"]
