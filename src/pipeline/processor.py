from __future__ import annotations

from typing import Iterable

from pydantic import BaseModel

from src.ingestion.store import IndexedMessage


class ConversationChunk(BaseModel):
    message_id: str
    text: str
    tokens: int


def chunk_messages(messages: Iterable[IndexedMessage], chunk_size: int = 200) -> Iterable[ConversationChunk]:
    for msg in messages:
        yield ConversationChunk(message_id=msg.message_id, text=msg.text, tokens=len(msg.text.split()))
