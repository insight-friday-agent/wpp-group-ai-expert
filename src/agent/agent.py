from __future__ import annotations

from typing import Iterable

from pydantic import BaseModel


class AgentResponse(BaseModel):
    answer: str
    citations: list[str]


class WhatsAppInsightsAgent:
    """Componente RAG que responde perguntas sobre o histórico do grupo."""

    def __init__(self, model_name: str, vector_store):
        self.model_name = model_name
        self.vector_store = vector_store

    def answer(self, question: str) -> AgentResponse:
        # placeholder: deve buscar embeddings e usar modelo
        top_chunks = self.vector_store.query([], top_k=5)
        citations = [entry.metadata.get("timestamp","?") for entry in top_chunks]
        return AgentResponse(
            answer=f"Ainda estou aprendendo. Perguntei ao modelo {self.model_name} e ele respondeu com dados frescos.",
            citations=citations,
        )
