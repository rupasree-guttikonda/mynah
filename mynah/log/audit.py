# mynah/log/audit.py
import sqlite3
import json
import os

DB_PATH = "audit.db"

def init_db():
    """Initializes the SQLite database and creates the turns table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS turns (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      transcript TEXT,
      frontmost_app TEXT,
      path TEXT,
      confidence REAL,
      tool TEXT,
      args TEXT, -- JSON string
      result TEXT,
      tokens_in INTEGER DEFAULT 0,
      tokens_out INTEGER DEFAULT 0,
      cost_usd REAL DEFAULT 0.0,
      latency_stt REAL,
      latency_route REAL,
      latency_exec REAL,
      confirmed BOOLEAN,
      repeated BOOLEAN DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()

def log_turn(turn_data: dict):
    """
    Logs a single turn interaction to the SQLite turns table.
    
    turn_data format:
    {
        "transcript": str,
        "frontmost_app": str,
        "path": str,
        "confidence": float,
        "tool": str,
        "args": dict,
        "result": str,
        "tokens_in": int,
        "tokens_out": int,
        "cost_usd": float,
        "latency_stt": float,
        "latency_route": float,
        "latency_exec": float,
        "confirmed": bool,
        "repeated": bool
    }
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Convert args dict to JSON string if present
    args_json = None
    if "args" in turn_data and turn_data["args"] is not None:
        args_json = json.dumps(turn_data["args"])
        
    cursor.execute("""
    INSERT INTO turns (
        transcript, frontmost_app, path, confidence, tool, args, result,
        tokens_in, tokens_out, cost_usd, latency_stt, latency_route, latency_exec,
        confirmed, repeated
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        turn_data.get("transcript"),
        turn_data.get("frontmost_app"),
        turn_data.get("path"),
        turn_data.get("confidence", 1.0),
        turn_data.get("tool"),
        args_json,
        turn_data.get("result"),
        turn_data.get("tokens_in", 0),
        turn_data.get("tokens_out", 0),
        turn_data.get("cost_usd", 0.0),
        turn_data.get("latency_stt"),
        turn_data.get("latency_route"),
        turn_data.get("latency_exec"),
        turn_data.get("confirmed", False),
        turn_data.get("repeated", False)
    ))
    conn.commit()
    conn.close()
