from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Set


class ChannelPolicy(Enum):
    """How a command should be restricted by channel."""

    ANY = "any"
    NON_SPAM_ONLY = "non_spam_only"
    SPAM_ONLY = "spam_only"
    NON_SPAM_OR_SPAM = "non_spam_or_spam"


@dataclass(frozen=True)
class GuildConfig:
    guild_id: int
    bot_name: str
    world_name: str

    # Normal command channels (shop, profile, inventory, etc.)
    allowed_non_spam_channel_ids: Optional[Set[int]] = None  # None => allow everywhere

    # Spam / grind channels (work, hunt, mine, gamble, etc.)
    allowed_spam_channel_ids: Optional[Set[int]] = None  # None => allow everywhere


# -----------------------------
# Current allowed guilds
# -----------------------------
VEYRA_GUILD_ID = 1419040189782818950
LILITH_GUILD_ID = 1334824535391997985
SELENE_GUILD_ID = 1275870089228320768

# Veyra server channels
VEYRA_INTRO_CHANNEL = 1419055325931376811

# Lilith server channels
LILITH_NON_SPAM_CHANNELS = {1334824538529071107, 1365055219146428467, 1462405749362786324}
LILITH_SPAM_CHANNELS = {1465704446213492944}
LILITH_INTRO_CHANNEL = 1351226530814103573
LILITH_LOTTERY_CHANNEL = 1465704663281045750


# Selene server channels
SELENE_NON_SPAM_CHANNELS = {1275870091002777643, 1434131335991136356}
SELENE_SPAM_CHANNELS = {1275870091002777642}
SELENE_INTRO_CHANNEL = 1462445147470954649

def get_config(guild_id: int) -> GuildConfig:
    """Return per-guild configuration.

    Right now this is hardcoded for 2 guilds.
    Later can be swapped this implementation to load from DB without touching command code
    """

    if guild_id == VEYRA_GUILD_ID:
        # Veyra's original guild: no channel restrictions
        return GuildConfig(
            guild_id=guild_id,
            bot_name="Veyra",
            world_name="Natlade",
            allowed_non_spam_channel_ids=None,
            allowed_spam_channel_ids=None,
        )

    if guild_id == LILITH_GUILD_ID:
        return GuildConfig(
            guild_id=guild_id,
            bot_name="Lilith",
            world_name="ABC",
            allowed_non_spam_channel_ids=LILITH_NON_SPAM_CHANNELS,
            allowed_spam_channel_ids=LILITH_SPAM_CHANNELS,
        )

    if guild_id == SELENE_GUILD_ID:
        return GuildConfig(
            guild_id=guild_id,
            bot_name="Selene",
            world_name="Lunarvile",
            allowed_non_spam_channel_ids=SELENE_NON_SPAM_CHANNELS,
            allowed_spam_channel_ids=SELENE_SPAM_CHANNELS
        )
    # Unknown guild fallback (safe defaults)
    return GuildConfig(
        guild_id=guild_id,
        bot_name="Veyra",
        world_name="Natlade",
        allowed_non_spam_channel_ids=None,
        allowed_spam_channel_ids=None,
    )


def is_channel_allowed(cfg: GuildConfig, channel_id: int, policy: ChannelPolicy) -> bool:
    """Centralized channel-allow logic.

    - None means "no restriction" for that list.
    - If both lists are None, everything is allowed.
    """

    non_spam = cfg.allowed_non_spam_channel_ids
    spam = cfg.allowed_spam_channel_ids

    # No restrictions at all
    if non_spam is None and spam is None:
        return True

    in_non_spam = non_spam is None or channel_id in non_spam
    in_spam = spam is None or channel_id in spam

    if policy == ChannelPolicy.ANY:
        return in_non_spam or in_spam

    if policy == ChannelPolicy.NON_SPAM_ONLY:
        return in_non_spam

    if policy == ChannelPolicy.SPAM_ONLY:
        return in_spam

    if policy == ChannelPolicy.NON_SPAM_OR_SPAM:
        return in_non_spam or in_spam

    return False
