from __future__ import annotations

from typing import Iterable

from pydantic import BaseModel

from src.retrieval.hybrid import HybridRetriever, RetrievalCandidate, SimpleReranker


class AgentResponse(BaseModel):
    answer: str
    citations: list[str]


class WhatsAppInsightsAgent:
    def __init__(self, model_name: str, retriever: HybridRetriever, reranker: SimpleReranker, context_size: int = 3):
        self.model_name = model_name
        self.retriever = retriever
        self.reranker = reranker
        self.context_size = context_size

    def answer(self, question: str) -> AgentResponse:
        candidates = self.retriever.retrieve(question, top_k=8)
        reranked = self.reranker.rerank(candidates, question)
        context_lines = self._format_context(reranked[: self.context_size])
        answer = self._compose_answer(question, context_lines)
        citations = [self._citation_from(candidate) for candidate in reranked[: self.context_size]]
        return AgentResponse(answer=answer, citations=citations)

    def _format_context(self, candidates: Iterable[RetrievalCandidate]) -> list[str]:
        lines: list[str] = []
        for candidate in candidates:
            source = candidate.entry.metadata.get("source", "local")
            score = candidate.combined_score
            lines.append(
                f"[{source}] ({score:.2f}) {candidate.entry.text[:280]}"
            )
        return lines

    def _compose_answer(self, question: str, context_lines: list[str]) -> str:
        if not context_lines:
            return f"Ainda não tenho dados suficientes sobre '{question}'. Me dá mais para analisar."
        joined = "\n".join(context_lines)
        return (
            f"Pergunta: {question}\n"
            f"Contexto usado:\n{joined}\n"
            "Resposta inspirada pelos pontos acima."
        )

    @staticmethod
    def _citation_from(candidate: RetrievalCandidate) -> str:
        return candidate.entry.metadata.get("source", "local")
