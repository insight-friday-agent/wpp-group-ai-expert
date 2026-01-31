from __future__ import annotations

import asyncio
from typing import Iterable

import httpx
from pydantic import BaseModel

from .store import MessageStore


class WhatsAppMessage(BaseModel):
    message_id: str
    author: str
    text: str
    timestamp: str


class UnofficialWhatsAppClient:
    """Abstrai o client com uma API não oficial (Twilio/Chat API/etc.)."""

    def __init__(self, api_url: str, token: str, store: MessageStore):
        self.api_url = api_url
        self.token = token
        self.store = store
        self.session = httpx.AsyncClient(timeout=60)

    async def fetch_new(self) -> Iterable[WhatsAppMessage]:
        """Busque novas mensagens. Substituir com o endpoint real."""
        response = await self.session.get(
            self.api_url,
            headers={"Authorization": f"Bearer {self.token}"},
        )
        response.raise_for_status()
        payload = response.json()
        for chunk in payload.get("messages", []):
            yield WhatsAppMessage(**chunk)

    async def run_forever(self, poll_interval: float = 5.0):
        while True:
            try:
                async for msg in self.fetch_new():
                    await self.store.save_message(msg)
            except httpx.HTTPError as exc:
                print("Erro na ingestão", exc)
            await asyncio.sleep(poll_interval)
