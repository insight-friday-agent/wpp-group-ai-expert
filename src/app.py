from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.agent.agent import WhatsAppInsightsAgent, AgentResponse
from src.config import settings
from src.retrieval.hybrid import HybridRetriever, SimpleReranker
from src.retrieval.pgvector_store import PgVectorStore


def build_store() -> PgVectorStore:
    return PgVectorStore(
        host=settings.pg_host,
        port=settings.pg_port,
        user=settings.pg_user,
        password=settings.pg_password,
        dbname=settings.pg_db,
        vector_dim=settings.vector_dim,
    )


class QueryRequest(BaseModel):
    question: str


class StatusResponse(BaseModel):
    message_count: int


app = FastAPI()
vector_store = build_store()
retriever = HybridRetriever(vector_store)
reranker = SimpleReranker()
agent = WhatsAppInsightsAgent(settings.model_name, retriever, reranker)


@app.post("/query", response_model=AgentResponse)
async def query_agent(payload: QueryRequest) -> AgentResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Pergunta vazia")
    return agent.answer(question)


@app.get("/status", response_model=StatusResponse)
async def status() -> StatusResponse:
    with vector_store.conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM notebook_chunks")
        result = cur.fetchone()
        count = int(result[0]) if result else 0
    return StatusResponse(message_count=count)


@app.on_event("shutdown")
def shutdown_event() -> None:
    vector_store.close()
