import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteDataStore:
    """Simple SQLite-backed storage for the web frontend/backend."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path(__file__).resolve().parent / "data" / "novasphere_web.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    action TEXT NOT NULL,
                    payload TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def record_event(self, category: str, action: str, payload: Optional[Dict[str, Any]] = None) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO events (category, action, payload) VALUES (?, ?, ?)",
                (category, action, json.dumps(payload or {}, ensure_ascii=False)),
            )

    def get_recent_events(self, limit: int = 25) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT category, action, payload, created_at FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        events: List[Dict[str, Any]] = []
        for row in rows:
            event_payload = row["payload"]
            try:
                event_data = json.loads(event_payload) if event_payload else {}
            except json.JSONDecodeError:
                event_data = {"raw": event_payload}
            events.append(
                {
                    "category": row["category"],
                    "action": row["action"],
                    "payload": event_data,
                    "created_at": row["created_at"],
                }
            )
        return events

    def save_snapshot(self, name: str, payload: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO snapshots (name, payload, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(name)
                DO UPDATE SET payload = excluded.payload, updated_at = excluded.updated_at
                """,
                (name, json.dumps(payload, ensure_ascii=False), datetime.utcnow().isoformat(timespec="seconds")),
            )

    def get_snapshot(self, name: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM snapshots WHERE name = ?", (name,)).fetchone()
        if row is None:
            return None
        try:
            return json.loads(row["payload"])
        except json.JSONDecodeError:
            return {"raw": row["payload"]}
