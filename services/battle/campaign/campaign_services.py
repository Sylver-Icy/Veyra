"""
Campaign Services

This module owns all campaign-specific progression logic for Veyra.
It is responsible for:
- Tracking a user's current campaign stage and progression
- Advancing campaign progress after victories
- Handling campaign-exclusive unlock conditions
- Resolving and distributing stage-based rewards
"""

from database.sessionmaker import Session

from models.users_model import User
from models.inventory_model import Items

from services.economy_services import add_gold
from services.inventory_services import give_item

from services.battle.campaign.campaign_config import CAMPAIGN_LEVELS,REWARD_CHART

from utils.emotes import GOLD_EMOJI

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
        int: Campaign stage (1–10).
    """
    with Session() as session:
        result = session.get(User, user_id)
        return result.campaign_stage if result else 1

def advance_campaign_stage(user_id: int) -> None:
    """
    Advance the user's campaign stage by one.

    Notes:
        - Campaign stages are capped at stage 10.
        - This function must only be called after a confirmed campaign victory.
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
    return get_campaign_stage(user_id) >= 10  # Campaign completion unlocks exclusive weapons


def give_stage_rewards(user_id: int) -> None:
    """
    Resolve and grant rewards for the user's current campaign stage.
    Rewards are defined declaratively in REWARD_CHART.
    """
    stage = get_campaign_stage(user_id)
    reward = REWARD_CHART.get(stage)

    # Each reward entry contains exactly one key-value pair
    key, value = next(iter(reward.items()))

    if key == "Gold":
        add_gold(user_id, value)
        return

    # Stage 10 unlock:
    # Signature weapon and spell unlock logic is handled by the battle/campaign system
    if key == "Unlock":
        return #user gets to lvl 10 that auto unlocks

    give_item(user_id, key, value)

def stage_reward_details(user_id: int):
    stage = get_campaign_stage(user_id)
    reward = REWARD_CHART.get(stage)

    # Each reward entry contains exactly one key-value pair
    key, value = next(iter(reward.items()))

    if key == "Gold":
        return f"You won {value}× {GOLD_EMOJI}!"

    if key == "Unlock":
        return (
            "You have proven yourself a warrior beyond doubt.\n"
            "As acknowledgment of your strength, I grant you my signature grimoire "
            "and the spell bound within it."
        )
    with Session() as session:
        item = session.get(Items, key)

    return f"You received {value}× {item.item_name}!"


def fetch_veyra_loadout(user_id: int) -> dict:
    """
    Fetch the campaign-specific loadout for Veyra at the user's current stage.

    Args:
        user_id (int): Discord user ID.

    Returns:
        dict: Loadout configuration for the current campaign stage.
    """
    stage = get_campaign_stage(user_id)
    loadout = CAMPAIGN_LEVELS.get(stage)
    return loadout