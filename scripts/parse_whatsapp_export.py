"""Parse exports do WhatsApp e converte em JSON estruturado para carregamento sintético."""
from __future__ import annotations

import argparse
import json
import re
import uuid
from datetime import datetime
from pathlib import Path

PATTERN = re.compile(r"^\[(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}:\d{2})\] ([^:]+?): (.*)$")


def parse_line(line: str):
    match = PATTERN.match(line)
    if not match:
        return None

    date_str, time_str, author, text = match.groups()
    timestamp = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%y %H:%M:%S").isoformat()
    return {
        "message_id": str(uuid.uuid4()),
        "timestamp": timestamp,
        "author": author.strip(),
        "text": text.strip(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse export WhatsApp para JSON de mensagens")
    parser.add_argument("input", type=Path, help="Arquivo .txt exportado do WhatsApp")
    parser.add_argument("--output", type=Path, default=Path("sample_data/exported_messages.json"))
    parser.add_argument("--limit", type=int, default=None, help="Limite de mensagens a exportar")
    args = parser.parse_args()

    messages = []
    for line in args.input.read_text(encoding="utf-8").splitlines():
        parsed = parse_line(line)
        if parsed:
            messages.append(parsed)
            if args.limit and len(messages) >= args.limit:
                break

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Geradas {len(messages)} mensagens em {args.output}")


if __name__ == "__main__":
    main()
