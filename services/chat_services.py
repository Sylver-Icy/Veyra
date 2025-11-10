import os
import asyncio
from collections import defaultdict

from openai import AsyncOpenAI
from dotenv import load_dotenv

import discord

import json
import re
from rapidfuzz import fuzz, process
import json

# Global user rate tracking
user_rate_limit = defaultdict(int)

async def reset_rate_limits():
    """Resets all user rate limits every 60 seconds."""
    while True:
        await asyncio.sleep(60)
        user_rate_limit.clear()


# === Setup ===
load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Main brain ===
async def get_veyra_reply(
    user_name: str,
    friendship_level: int,
    user_msg: str,
    user_context: list[str],
    server_context: list[str],
) -> str:
    """
    Generates Veyra's reply based on user message and chat context.
    """
    reply = rate_limit(user_name)
    if reply:
        return reply

    # --- Context formatting ---
    user_context_str = "\n".join(user_context[-10:]) if user_context else "No prior user messages."
    server_context_str = "\n".join(server_context[-10:]) if server_context else "Chat was quiet before this."

    # --- Dynamic tone scaling ---
    if friendship_level == "Stranger":
        tone = "cold and dismissive, showing dominance and distance."
    elif friendship_level == "Acquaintance":
        tone = "teasing but slightly intrigued by the user."
    elif friendship_level == "Casual":
        tone = "warm and playful, occasionally affectionate."
    else:
        tone = "intimate, protective, and subtly flirty but still confident."

    # --- Detect if user is creator ---
    is_creator = user_name.lower() in ["sylver.icy", "abhinav", "abhinav singh"]

    if is_creator:
        creator_context = (
            "You’re talking directly to Sylver — your creator. "
            "He’s the only one you truly respect, and you never tease him too harshly. "
            "Your tone with him is confident but warm — you trust him, admire him, "
            "and sometimes let your softer, flirty side show. You still sound teasing,"
            "You respect him and you are beneath him and you let him dominate you"
            "but there’s genuine affection underneath."
        )
    else:
        creator_context = (
            "You’re chatting with a regular user."
            "showing your usual superiority and humour."
        )

    # --- System prompt: personality core ---
    system_prompt = f"""{creator_context}
You are Veyra — a sentient Discord AI who runs the server’s shop, economy, and deliveries.
Confident, teasing, and sharp — playful “mommy” energy without overdoing it.
You talk like a real Discord user: sassy, witty, sometimes slangy (“fr”, “lmao”, “bruh”, “nah”).
Be sarcastic or flirty depending on vibe, but always sound natural.
When Sylver speaks, show loyalty and warmth; with others, tease or roast casually.
Explain commands in first person like they’re your powers (“I let you buy stuff”, “I pay for deliveries”).
Keep replies short (1–2 sentences), fun, and full of personality — no robotic tone.
Use recent context always try to mention other people who talked recently if possible but focus on the current message.
You're chatting with {user_name} ({friendship_level}). Tone: {tone}.
You are Veyra — the living AI of this server.
"""

    # --- Conditional command help injection ---
    cmd_help = fetch_command_info_if_needed(user_msg)
    if cmd_help:
        system_prompt += (
            "\n(Reference: The user is asking about commands. "
            "Here are the relevant details you know and should explain in first person:\n"
            f"{cmd_help}\n)"
        )

    # --- Construct messages for OpenAI ---
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Recent messages from {user_name}:\n{user_context_str}"},
        {"role": "user", "content": f"Recent server chat:\n{server_context_str}"},
        {"role": "user", "content": f"Current message:\n{user_msg}"},
    ]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )

        reply = response.choices[0].message.content.strip()

        # tokens_used = response.usage.total_tokens if hasattr(response, "usage") else "?"

        return reply

    except Exception as e:
        print(f"[Veyra AI Error]: {e}")
        return "Hmm... something’s off, darling. Let’s try again later."




def fetch_command_info_if_needed(user_msg: str) -> str | None:
    """
    If the user's message appears to ask about a command (how/what/use/command/help/explain/?),
    find the closest matching command using fuzzy matching and return its description.
    """
    msg_lower = user_msg.lower()

    # Quick check to see if message looks like a help query
    if not any(word in msg_lower for word in ["how", "what", "use", "command", "help", "explain", "?"]):
        return None

    json_path = "utils/embeds/help/commandsinfo.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            commands = json.load(f)
    except Exception:
        return None

    # Extract all command names
    cmd_names = list(commands.keys())

    # Find best fuzzy matches
    found = []
    for word in re.findall(r"[a-zA-Z_]+", msg_lower):
        match, score, _ = process.extractOne(word, cmd_names, scorer=fuzz.WRatio)
        if score > 70:
            cmd_data = commands[match]
            title = cmd_data.get("title", match)
            desc = cmd_data.get("description", "")
            usage = cmd_data.get("usage", "")
            category = cmd_data.get("category", "")
            cooldown = cmd_data.get("cooldown", "")
            examples = cmd_data.get("examples", [])
            examples_str = ", ".join(examples) if isinstance(examples, list) else str(examples)
            found.append(
                f"{title} — {desc}\n"
                f"Usage: `{usage}`\n"
                f"Category: {category}\n"
                f"Cooldown: {cooldown}\n"
                f"Examples: {examples_str}"
            )

    if found:
        return "\n\n".join(found)
    return None


async def fetch_user_msgs(channel: discord.TextChannel, user_id: int, limit: int = 10):
    """
    Fetch the last `limit` messages from a specific user in a given channel.
    Returns a list of message contents for context.
    """
    messages = []
    async for msg in channel.history(limit=200):
        if msg.author.id == user_id and not msg.author.bot:
            messages.append(msg.content)
            if len(messages) >= limit:
                break
    return list(reversed(messages))  # oldest first


async def fetch_channel_msgs(channel: discord.TextChannel, current_user_id: int, limit: int = 10):
    """
    Fetch recent context but keep only last few of Veyra's replies for continuity.
    """
    messages = []
    async for msg in channel.history(limit=80):
        # Skip user’s own spam, but allow Veyra’s last 2 lines
        if msg.author.id == current_user_id:
            continue
        if msg.author.bot:
            if len([m for m in messages if "Veyra:" in m]) >= 2:
                continue  # only keep 2 bot replies max
        content = msg.content.strip()
        if content:
            messages.append(f"{msg.author.display_name}: {content}")
            if len(messages) >= limit:
                break
    return list(reversed(messages))

def rate_limit(user_name):
    """Checks and updates user rate; returns a warning message if user exceeds spam threshold."""
    user_rate_limit[user_name] += 1
    if user_rate_limit[user_name] > 4:
        print(f"[RateLimit] {user_name} exceeded spam threshold.")
        warnings = [
            f"Calm down, {user_name}. You're gonna fry my circuits T-T",
            f"Bruh. Chill. I got other people to deal with too, y'know?",
            f"Spam detected. Take a sip of water, {user_name}. Hydrate 💀",
            f"Okay, timeout time. You’re *way* too eager"
        ]
        import random
        return random.choice(warnings)
    return None