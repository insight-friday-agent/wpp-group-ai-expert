"""Executa consultas de validação e julga as respostas do agente."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.agent.agent import WhatsAppInsightsAgent
from src.config import settings
from src.retrieval.hybrid import HybridRetriever, SimpleReranker
from src.retrieval.pgvector_store import PgVectorStore


QUERIES = [
    {
        "question": "Quais ofertas o Qual Notebook Comprar menciona?",
        "keywords": ["notebook", "ofert"],
        "citation_contains": ["qualnotebook", "quenotebook", "carlos"],
    },
    {
        "question": "O que o export do WhatsApp relata sobre eventos recentes?",
        "keywords": ["culto", "event"],
        "citation_contains": ["qualnotebook", "quenotebook"],
    },
]


def get_store() -> PgVectorStore:
    return PgVectorStore(
        host=os.getenv("PGHOST", settings.pg_host),
        port=int(os.getenv("PGPORT", settings.pg_port)),
        user=os.getenv("PGUSER", settings.pg_user),
        password=os.getenv("PGPASSWORD", settings.pg_password),
        dbname=os.getenv("PGDATABASE", settings.pg_db),
        vector_dim=int(os.getenv("VECTOR_DIM", settings.vector_dim)),
    )


def matches_keywords(text: str, keywords: list[str]) -> bool:
    normalized = text.lower()
    return any(keyword.lower() in normalized for keyword in keywords)


def matches_citations(citations: list[str], patterns: list[str]) -> bool:
    if not patterns:
        return True
    normalized = " ".join(citations).lower()
    return any(pattern.lower() in normalized for pattern in patterns)


def main() -> int:
    store = get_store()
    retriever = HybridRetriever(store)
    reranker = SimpleReranker()
    agent = WhatsAppInsightsAgent(settings.model_name, retriever, reranker)
    overall = True
    for query in QUERIES:
        response = agent.answer(query["question"])
        answer = response.answer
        citations = response.citations
        passed_keywords = matches_keywords(answer, query["keywords"])
        passed_citation = matches_citations(citations, query.get("citation_contains", []))
        passed = passed_keywords and passed_citation
        overall = overall and passed
        print("\nQuery:", query["question"])
        print("Resposta:", answer)
        print("Citations:", citations)
        print(
            "Judgement:",
            "PASS" if passed else "FAIL",
            f"(keywords={'Y' if passed_keywords else 'N'}, citations={'Y' if passed_citation else 'N'})",
        )
    store.close()
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
