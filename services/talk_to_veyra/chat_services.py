from __future__ import annotations

import os
from typing import Any

import aiohttp
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv("veyra.env")


class ConversationServiceError(RuntimeError):
    """Raised when the external conversation service cannot be reached cleanly."""


class ConversationService:
    def __init__(self, endpoint: str | None = None):
        self.endpoint = endpoint or os.getenv("CONVO_MODEL_URL", "http://127.0.0.1:8000/chat")
        self.api_key = os.getenv("CONVO_MODEL_API_KEY")
        if not self.api_key:
            raise RuntimeError("CONVO_MODEL_API_KEY is required for talk-to-Veyra chat.")

        base_url = self.endpoint.removesuffix("/chat")
        self.health_endpoint = f"{base_url}/health"
        self._session: aiohttp.ClientSession | None = None
        self._timeout = aiohttp.ClientTimeout(total=60, connect=5, sock_connect=5, sock_read=25)

    async def start(self) -> None:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    async def is_available(self) -> bool:
        await self.start()
        assert self._session is not None

        try:
            async with self._session.get(self.health_endpoint) as resp:
                return resp.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False

    async def get_reply(self, payload: dict[str, Any]):
        await self.start()
        assert self._session is not None

        try:
            async with self._session.post(
                self.endpoint,
                json=payload,
                headers={"api-key": self.api_key},
            ) as resp:
                if resp.status != 200:
                    detail = (await resp.text()).strip()
                    raise ConversationServiceError(
                        f"Conversation service returned HTTP {resp.status}: {detail or 'no response body'}"
                    )
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise ConversationServiceError(f"Conversation service request failed: {exc}") from exc


brain = ConversationService()


async def handle_user_message(message: str, user: dict, message_history: list):
    payload = {
        "message": message,
        "user": user,
        "message_history": message_history,
    }

    reply = await brain.get_reply(payload)
    if not isinstance(reply, str):
        return None

    reply = reply.strip()
    return reply if reply else None


async def fetch_channel_msgs(channel: discord.TextChannel, limit: int = 10, bot_id: int | None = None):
    """Fetch recent structured chat context with explicit user/assistant roles."""
    messages = []
    bot_reply_count = 0

    async for msg in channel.history(limit=80):
        content = msg.content.strip()
        if not content:
            continue

        is_self_bot = bool(msg.author.bot and (bot_id is None or msg.author.id == bot_id))
        if msg.author.bot and not is_self_bot:
            continue

        if is_self_bot:
            if bot_reply_count >= 2:
                continue
            bot_reply_count += 1
            role = "assistant"
        else:
            role = "user"

        messages.append(
            {
                "author": msg.author.display_name,
                "role": role,
                "content": content,
            }
        )

        if len(messages) >= limit:
            break

    return list(reversed(messages))