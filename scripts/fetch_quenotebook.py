"""Baixa textos do https://quenotebookcomprar.com.br/ para gerar dados sintéticos."""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup


def extract_text_blocks(html: str, limit: int) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    selectors = ["main h2", "main h3", "main p", "main li"]
    texts: list[str] = []
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(separator=" ", strip=True)
            if len(text) < 60:
                continue
            if text in texts:
                continue
            texts.append(text)
            if len(texts) >= limit:
                return texts
    return texts


def generate_payload(texts: list[str], source_url: str) -> list[dict[str, str]]:
    now = datetime.now(timezone.utc).isoformat()
    payload = []
    for idx, snippet in enumerate(texts, start=1):
        payload.append(
            {
                "message_id": f"site-{uuid.uuid4()}",
                "timestamp": now,
                "author": "QualNotebookComprar",
                "text": snippet,
                "source_url": source_url,
                "position": str(idx),
            }
        )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrai trechos do site para criar dados sintéticos.")
    parser.add_argument("--url", type=str, default="https://quenotebookcomprar.com.br/", help="URL base do site")
    parser.add_argument(
        "--limit",
        type=int,
        default=12,
        help="Quantidade máxima de blocos extraídos",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("sample_data/quenotebook.json"),
        help="Arquivo JSON de saída",
    )
    args = parser.parse_args()

    response = httpx.get(args.url, timeout=30)
    response.raise_for_status()
    blocks = extract_text_blocks(response.text, args.limit)
    payload = generate_payload(blocks, args.url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Geradas {len(payload)} mensagens sintéticas em {args.output}")


if __name__ == "__main__":
    main()
