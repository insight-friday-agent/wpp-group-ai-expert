from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException

from .agent.agent import WhatsAppInsightsAgent, AgentResponse
from .pipeline.store import VectorStore, VectorStoreEntry

app = FastAPI()

# Placeholder vector store (keep in-memory)
class InMemoryVectorStore(VectorStore):
    def __init__(self):
        self.entries: list[VectorStoreEntry] = []

    def add(self, entries: list[VectorStoreEntry]) -> None:
        self.entries.extend(entries)

    def query(self, embedding: list[float], top_k: int = 5):
        return self.entries[:top_k]

store = InMemoryVectorStore()
agent = WhatsAppInsightsAgent(model_name="claude-sonnet", vector_store=store)

@app.post("/query")
async def query_agent(question: str) -> AgentResponse:
    if not question.strip():
        raise HTTPException(status_code=400, detail="Pergunta vazia")
    return agent.answer(question)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
