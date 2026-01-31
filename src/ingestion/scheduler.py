from __future__ import annotations

import asyncio
import os

from .client import UnofficialWhatsAppClient
from .store import MessageStore, IndexedMessage


async def main():
    store = MessageStore(os.environ.get("INBOX_DB", "./data/messages.db"))
    client = UnofficialWhatsAppClient(
        api_url=os.environ.get("WHATSAPP_API_URL", "https://api.placehold.it/messages"),
        token=os.environ.get("WHATSAPP_API_TOKEN", "token-placeholder"),
        store=store,
    )
    print("Ingestão iniciada")
    await client.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
