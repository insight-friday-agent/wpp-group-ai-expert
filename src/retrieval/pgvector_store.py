from __future__ import annotations

import json
from typing import Iterable

import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor

from src.pipeline.store import VectorSearchResult, VectorStoreEntry, VectorStore


class PgVectorStore(VectorStore):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "postgres",
        dbname: str = "wpp",
        vector_dim: int = 8,
    ):
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
        )
        self.vector_dim = vector_dim

    def _vector_literal(self, vector: list[float]) -> str:
        vals = vector or [0.0] * self.vector_dim
        components = ",".join(str(float(v)) for v in vals)
        return f"[{components}]"

    def _ensure_table(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS notebook_chunks (
                    id SERIAL PRIMARY KEY,
                    message_id TEXT UNIQUE,
                    text TEXT NOT NULL,
                    source TEXT,
                    metadata JSONB,
                    timestamp TIMESTAMPTZ,
                    embedding vector(%s)
                )
                """,
                (self.vector_dim,),
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_notebook_chunks_embedding
                ON notebook_chunks USING ivfflat (embedding vector_l2_ops)
                """,
            )
        self.conn.commit()

    def add(self, entries: Iterable[VectorStoreEntry]) -> None:
        self._ensure_table()
        with self.conn.cursor() as cur:
            for entry in entries:
                vector_literal = self._vector_literal(entry.embedding or [0.0] * self.vector_dim)
                cur.execute(
                    """
                    INSERT INTO notebook_chunks (message_id, text, source, metadata, timestamp, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s::vector)
                    ON CONFLICT (message_id) DO UPDATE
                    SET text = EXCLUDED.text,
                        source = EXCLUDED.source,
                        metadata = EXCLUDED.metadata,
                        timestamp = EXCLUDED.timestamp,
                        embedding = EXCLUDED.embedding
                    """,
                    (
                        entry.message_id,
                        entry.text,
                        entry.metadata.get("source"),
                        json.dumps(entry.metadata),
                        entry.timestamp,
                        vector_literal,
                    ),
                )
        self.conn.commit()

    def query(self, embedding: list[float], top_k: int = 5) -> Iterable[VectorSearchResult]:
        self._ensure_table()
        literal = self._vector_literal(embedding or [0.0] * self.vector_dim)
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT message_id, text, source, metadata, timestamp,
                       embedding <=> %s::vector AS distance
                FROM notebook_chunks
                ORDER BY distance
                LIMIT %s
                """,
                (literal, top_k),
            )
            rows = cur.fetchall()
        results: list[VectorSearchResult] = []
        for row in rows:
            meta = {} if row["metadata"] is None else row["metadata"]
            entry = VectorStoreEntry(
                message_id=row["message_id"],
                text=row["text"],
                metadata={
                    **{k: str(v) for k, v in meta.items()},
                    "source": row.get("source") or meta.get("source", "pgvector"),
                },
                timestamp=row.get("timestamp"),
            )
            results.append(VectorSearchResult(entry=entry, distance=row.get("distance")))
        return results

    def close(self) -> None:
        self.conn.close()
