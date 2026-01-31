from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel


class IndexedMessage(BaseModel):
    message_id: str
    author: str
    text: str
    timestamp: str
    stored_at: str


class MessageStore:
    def __init__(self, path: Path | str = "./data/messages.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                author TEXT,
                text TEXT,
                timestamp TEXT,
                stored_at TEXT
            )
            """
        )
        self.conn.commit()

    def save_message(self, message: IndexedMessage) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO messages (message_id, author, text, timestamp, stored_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (message.message_id, message.author, message.text, message.timestamp),
        )
        self.conn.commit()

    def get_recent(self, limit: int = 100) -> Iterable[IndexedMessage]:
        cursor = self.conn.execute(
            "SELECT message_id, author, text, timestamp, stored_at FROM messages ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        for row in cursor:
            yield IndexedMessage(**dict(zip(cursor.description, row)))
