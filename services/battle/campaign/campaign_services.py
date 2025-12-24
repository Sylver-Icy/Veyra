"""
Campaign Services

This module owns all campaign-specific progression logic for Veyra.
It is responsible for:
- Tracking a user's current campaign stage
- Advancing campaign progress on victory
- Determining campaign-only unlocks
- Distributing stage-based rewards
"""

from database.sessionmaker import Session
from models.users_model import User

from services.economy_services import add_gold
from services.inventory_services import give_item

from services.battle.campaign.campaign_config import CAMPAIGN_LEVELS,REWARD_CHART

# --------------------------------------------------
# Campaign reward table
# --------------------------------------------------
# Maps campaign stage -> reward definition.
#
# Reward format rules:
# - {"Gold": amount}         -> grants raw gold
# - {item_id: amount}       -> grants inventory items
# - {"Unlock": 0}           -> special one-time unlock (handled separately)
#
# This table is intentionally data-driven to avoid
# hardcoding reward logic per stage.


def get_campaign_stage(user_id: int) -> int:
    """
    Fetch the user's current campaign stage.

    Args:
        user_id (int): Discord user ID.

    Returns:
        int: Campaign stage (0–10).
             Stage 0 indicates campaign not started.
    """
    with Session() as session:
        result = session.get(User, user_id)
        return result.campaign_stage if result else 0

def advance_campaign_stage(user_id: int) -> None:
    """
    Advance the user's campaign stage by one.

    Notes:
    - Campaign stages are capped at 10.
    - This function should only be called after a campaign victory.
    """
    with Session() as session:
        user = session.get(User, user_id)
        if user:
            if user.campaign_stage < 10:
                user.campaign_stage += 1
            session.commit()


def allow_campaign_weapons(user_id: int) -> bool:
    """
    Check whether the user has unlocked campaign-exclusive weapons.

    Returns:
        bool: True if the user has completed the campaign (stage >= 10).
    """
    return get_campaign_stage(user_id) >=10


def give_stage_rewards(user_id: int) -> None:
    """
    Grant the appropriate reward for the user's current campaign stage.

    This function resolves rewards based on REWARD_CHART and applies them
    using the correct service (economy, inventory, or unlocks).

    Assumptions:
    - Campaign stage is within 1–10.
    - Rewards are granted once per stage progression.
    """
    stage = get_campaign_stage(user_id)
    reward = REWARD_CHART.get(stage)

    # Each reward entry contains exactly one key-value pair
    key, value = next(iter(reward.items()))

    if key == "Gold":
        add_gold(user_id, value)
        return

    # Stage 10 unlock:
    # Signature weapon and spell unlock logic is handled elsewhere
    if key == "Unlock":
        return #user gets to lvl 10 that auto unlocks

    give_item(user_id, key, value)


def fetch_veyra_loadout(user_id: int) -> dict:
    stage = get_campaign_stage(user_id)
    loadout = CAMPAIGN_LEVELS.get(stage)
    return loadout