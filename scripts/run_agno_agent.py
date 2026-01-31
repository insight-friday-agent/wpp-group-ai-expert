"""Executa o agente Agno usando um modelo local Ollama."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Iterable

from src.agent.agent import WhatsAppInsightsAgent
from src.config import settings
from src.retrieval.hybrid import HybridRetriever, SimpleReranker, RetrievalCandidate
from src.retrieval.pgvector_store import PgVectorStore

MODEL = os.getenv("OLLAMA_MODEL", "llama3")
PROMPT_TEMPLATE = """
## Your Role
RAG specialist for the Comunidade WhatsApp group. Use recent chunks (last 7 days) and cite timestamps.
## Input
- question: {question}
- context: {context}
## Process
1. Review the provided context.
2. Answer clearly in Portuguese.
3. If information is missing, say so and reference what you do have.
## Output
- answer: text
- citations: list
"""


def build_store() -> PgVectorStore:
    return PgVectorStore(
        host=settings.pg_host,
        port=settings.pg_port,
        user=settings.pg_user,
        password=settings.pg_password,
        dbname=settings.pg_db,
        vector_dim=settings.vector_dim,
    )


def format_context(candidates: Iterable[RetrievalCandidate]) -> str:
    lines = []
    for candidate in candidates:
        source = candidate.entry.metadata.get("source", "local")
        score = candidate.combined_score
        ts = candidate.entry.timestamp or "?"
        lines.append(f"[{source}] ({score:.2f}) {ts} | {candidate.entry.text}")
    return "\n".join(lines)


def call_ollama(prompt: str) -> str:
    if not shutil.which("ollama"):
        raise RuntimeError("Ollama não está instalado ou não está no PATH. Rode o instalador e certifique-se de que `ollama` é acessível.")
    cmd = ["ollama", "run", MODEL, "--prompt", prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Ollama falhou: {result.stderr.strip()}")
    return result.stdout.strip()


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python scripts/run_agno_agent.py \"Pergunta\"")
        return 1
    question = sys.argv[1].strip()
    store = build_store()
    retriever = HybridRetriever(store)
    reranker = SimpleReranker()
    agent = WhatsAppInsightsAgent(settings.model_name, retriever, reranker)
    candidates = reranker.rerank(retriever.retrieve(question, top_k=8), question)
    context = format_context(candidates[:3])
    prompt = PROMPT_TEMPLATE.format(question=question, context=context)
    try:
        answer = call_ollama(prompt)
    except RuntimeError as exc:
        print("Erro ao chamar Ollama:", exc)
        return 1
    print("=== Prompt ===")
    print(prompt)
    print("\n=== Ollama answer ===")
    print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
