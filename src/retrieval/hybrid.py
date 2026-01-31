from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from src.pipeline.store import VectorStoreEntry, VectorStore
from src.retrieval.vectorizer import text_to_vector


@dataclass
class RetrievalCandidate:
    entry: VectorStoreEntry
    distance: float | None
    text_score: float
    combined_score: float


class HybridRetriever:
    def __init__(self, vector_store: VectorStore, vector_weight: float = 0.6, multiplier: int = 2):
        self.vector_store = vector_store
        self.vector_weight = vector_weight
        self.multiplier = multiplier
        self.vector_dim = getattr(vector_store, "vector_dim", 8)

    def retrieve(self, question: str, top_k: int = 5) -> list[RetrievalCandidate]:
        vector = text_to_vector(question, dim=self.vector_dim)
        raw = self.vector_store.query(vector, top_k=top_k * self.multiplier)
        tokens = self._tokenize(question)
        candidates: list[RetrievalCandidate] = []
        for result in raw:
            text_score = self._text_score(result.entry.text, tokens)
            similarity = self._similarity(result.distance)
            combined = self.vector_weight * similarity + (1 - self.vector_weight) * text_score
            candidate = RetrievalCandidate(
                entry=result.entry,
                distance=result.distance,
                text_score=text_score,
                combined_score=combined,
            )
            candidates.append(candidate)
        candidates.sort(key=lambda candidate: candidate.combined_score, reverse=True)
        return candidates[:top_k]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [token for token in re.findall(r"\w+", text.lower()) if token]

    @staticmethod
    def _text_score(text: str, tokens: Iterable[str]) -> float:
        tokens = list(tokens)
        if not tokens:
            return 0.0
        text_tokens = set(re.findall(r"\w+", text.lower()))
        matches = sum(1 for token in tokens if token in text_tokens)
        return matches / len(tokens)

    @staticmethod
    def _similarity(distance: float | None) -> float:
        if distance is None:
            return 0.0
        return 1.0 / (1.0 + distance)


class SimpleReranker:
    def rerank(self, candidates: list[RetrievalCandidate], question: str) -> list[RetrievalCandidate]:
        now = datetime.now(timezone.utc)
        for candidate in candidates:
            recency = 0.0
            timestamp_value = candidate.entry.timestamp
            if timestamp_value:
                try:
                    if isinstance(timestamp_value, datetime):
                        recorded = timestamp_value
                    else:
                        recorded = datetime.fromisoformat(timestamp_value)
                    if recorded.tzinfo is None:
                        recorded = recorded.replace(tzinfo=timezone.utc)
                    age_seconds = (now - recorded).total_seconds()
                    recency = max(0.0, 1.0 - min(age_seconds / 86400.0, 1.0))
                except (ValueError, TypeError):
                    recency = 0.0
            candidate.combined_score += 0.1 * recency
        candidates.sort(key=lambda candidate: candidate.combined_score, reverse=True)
        return candidates
