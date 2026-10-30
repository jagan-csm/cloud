import sqlite3, json, os
from datetime import datetime, timezone
from app.config import DATABASE

def connect():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
            service TEXT NOT NULL, severity TEXT NOT NULL, title TEXT NOT NULL,
            details TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active')""")

def create_incident(service, severity, title, details):
    with connect() as db:
        cur = db.execute("INSERT INTO incidents(created_at,service,severity,title,details) VALUES(?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), service, severity, title, json.dumps(details)))
        return cur.lastrowid

def list_incidents():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM incidents ORDER BY id DESC LIMIT 100")]

def resolve_incidents():
    with connect() as db:
        db.execute("UPDATE incidents SET status='resolved' WHERE status='active'")
