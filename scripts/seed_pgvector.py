"""Popula o Postgres+pgvector com os dados sintéticos preparados."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.pipeline.store import VectorStoreEntry
from src.retrieval.pgvector_store import PgVectorStore
from src.retrieval.vectorizer import text_to_vector


SAMPLE_FILES = [
    Path("sample_data/messages_template.json"),
    Path("sample_data/whatsapp_export.json"),
    Path("sample_data/quenotebook.json"),
]


def load_messages(files: list[Path]) -> Iterable[dict]:
    for path in files:
        if not path.exists():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        for record in raw:
            yield record


def build_entry(message: dict, vector_dim: int) -> VectorStoreEntry:
    text = message.get("text", "")
    if not text:
        text = "(sem texto)"
    timestamp = message.get("timestamp")
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()
    metadata = {
        "author": message.get("author", "import"),
        "source": message.get("source_url") or message.get("author", "import"),
    }
    embedding = text_to_vector(text, dim=vector_dim)
    return VectorStoreEntry(
        message_id=message.get("message_id", message.get("id", str(os.urandom(8).hex()))),
        text=text,
        metadata=metadata,
        timestamp=timestamp,
        embedding=embedding,
    )


def main() -> None:
    store = PgVectorStore(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "postgres"),
        dbname=os.getenv("PGDATABASE", "wpp"),
        vector_dim=int(os.getenv("VECTOR_DIM", "8")),
    )
    entries = [build_entry(msg, store.vector_dim) for msg in load_messages(SAMPLE_FILES)]
    if not entries:
        print("Nenhuma mensagem encontrada para inserir.")
        return
    store.add(entries)
    print(f"Inseridos {len(entries)} registros em pgvector.")
    store.close()


if __name__ == "__main__":
    main()
