import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class LogDataStore:
    """Log-file storage for CLI and GUI modes."""

    def __init__(self, scope: str = "novasphere"):
        self.scope = scope
        self.log_dir = Path(__file__).resolve().parents[2] / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"{scope}_data.log"

    def log_event(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        record = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "event": event_type,
            "payload": payload or {},
        }
        with self.log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def read_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.log_file.exists():
            return []

        events: List[Dict[str, Any]] = []
        with self.log_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    events.append({"raw": line})
                if limit and len(events) >= limit:
                    break
        return events
