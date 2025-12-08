import aiohttp
import discord
import os

from dotenv import load_dotenv
load_dotenv()

from services.talk_to_veyra.call_service import run_service

class ConversationService:
    def __init__(self, endpoint):
        self.endpoint = endpoint


    async def get_reply(self, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json=payload,
                headers={"api_key": os.getenv("CONVO_MODEL_API_KEY")}
            ) as resp:
                return await resp.json()

brain = ConversationService("http://127.0.0.1:8000/chat")

async def handle_user_message(message: str, frndship_title: str, user_id: int, user_name: str, message_history: list):
    payload = {
        "text": message,
        "frndship_title": frndship_title,
        "user_id": user_id,
        "user_name": user_name,
        "message_history": message_history
    }

    reply = await brain.get_reply(payload)
    if reply in ("LABEL_0", "LABEL_1", "LABEL_2", "LABEL_3", "LABEL_4", "LABEL_5", "LABEL_6", "LABEL_7"):
        return run_service(reply, user_id)

    return reply

async def fetch_channel_msgs(channel: discord.TextChannel, limit: int = 10, bot_id: int = None):
    """
    Fetch recent context but keep only last 2 of Veyra's replies.
    """
    messages = []
    bot_reply_count = 0

    async for msg in channel.history(limit=80):
        content = msg.content.strip()
        if not content:
            continue

        # Identify bot messages properly
        is_self_bot = msg.author.bot and (bot_id is None or msg.author.id == bot_id)

        if is_self_bot:
            if bot_reply_count >= 2:
                continue
            bot_reply_count += 1

        messages.append(f"{msg.author.display_name}: {content}")

        if len(messages) >= limit:
            break

    return list(reversed(messages))
