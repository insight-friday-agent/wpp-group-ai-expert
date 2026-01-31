from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class VectorStoreEntry:
    message_id: str
    text: str
    metadata: dict[str, str]
    timestamp: str | None = None
    embedding: list[float] | None = None


@dataclass
class VectorSearchResult:
    entry: VectorStoreEntry
    distance: float | None = None


class VectorStore:
    """Interface para um vetor store."""

    def add(self, entries: Iterable[VectorStoreEntry]) -> None:
        raise NotImplementedError

    def query(self, embedding: list[float], top_k: int = 5) -> Iterable[VectorSearchResult]:
        raise NotImplementedError
