from __future__ import annotations

from typing import Iterable


class VectorStoreEntry:
    def __init__(self, message_id: str, embedding: list[float], metadata: dict[str, str]):
        self.message_id = message_id
        self.embedding = embedding
        self.metadata = metadata


class VectorStore:
    """Interface para um vetor store; componentes concretos devem implementar."""

    def add(self, entries: Iterable[VectorStoreEntry]) -> None:
        raise NotImplementedError

    def query(self, embedding: list[float], top_k: int = 5) -> Iterable[VectorStoreEntry]:
        raise NotImplementedError
