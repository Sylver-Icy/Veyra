"""
Handles weapon/spell loadout updates & retrieval for battle system.
Includes validation for allowed weapons/spells, creates loadouts for new users,
and updates existing entries. Uses SQLAlchemy sessions.
"""

from database.sessionmaker import Session

from models.users_model import BattleLoadout

from services.battle.campaign.campaign_services import get_campaign_stage

from domain.battle.rules import (
    get_allowed_weapons,
    get_allowed_spells,
    get_weapon_unlock_stage,
    get_spell_unlock_stage,
    get_weapon_label,
    get_spell_label,
)

def _normalize_input(value: str) -> str:
    """
    Normalize user input for weapons/spells.
    - lowercase
    - remove spaces and underscores
    """
    return value.lower().replace(" ", "").replace("_", "")

def update_loadout(user_id: int, weapon: str = None, spell: str = None):
    """
    Update or create a player's battle loadout.

    - Accepts optional weapon and/or spell
    - Validates provided values only
    - Preserves existing values if not supplied
    Returns structured result for UI usage.
    """

    weapon_key = _normalize_input(weapon) if weapon else None
    spell_key = _normalize_input(spell) if spell else None

    allowed_weapons = get_allowed_weapons()
    allowed_spells = get_allowed_spells()

    if weapon_key and weapon_key not in allowed_weapons:
        return {
            "success": False,
            "message": f"Invalid weapon: {weapon}"
        }

    if spell_key and spell_key not in allowed_spells:
        return {
            "success": False,
            "message": f"Invalid spell: {spell}"
        }

    stage = get_campaign_stage(user_id)

    if weapon_key:
        required_stage = get_weapon_unlock_stage(weapon_key)
        if stage < required_stage:
            return {
                "success": False,
                "message": f"{get_weapon_label(weapon_key)} unlocks at campaign stage {required_stage}"
            }

    if spell_key:
        required_stage = get_spell_unlock_stage(spell_key)
        if stage < required_stage:
            return {
                "success": False,
                "message": f"{get_spell_label(spell_key)} unlocks at campaign stage {required_stage}"
            }

    with Session() as session:
        warrior = session.get(BattleLoadout, user_id)

        if warrior:
            if weapon_key:
                warrior.weapon = weapon_key
            if spell_key:
                warrior.spell = spell_key

            session.commit()

            return {
                "success": True,
                "weapon": warrior.weapon,
                "spell": warrior.spell,
                "message": "Loadout updated"
            }

        # Create new loadout (fallback to defaults if missing)
        new_entry = BattleLoadout(
            user_id=user_id,
            weapon=weapon_key or "trainingblade",
            spell=spell_key or "nightfall"
        )

        session.add(new_entry)
        session.commit()

        return {
            "success": True,
            "weapon": new_entry.weapon,
            "spell": new_entry.spell,
            "message": "Loadout created"
        }

def fetch_loadout(user_id: int):
    """
    Fetch the user's equipped weapon & spell.
    Returns default loadout if user has none.
    """
    with Session() as session:
        warrior = session.get(BattleLoadout, user_id)
        if warrior:
            return (warrior.weapon, warrior.spell)

        #default loadout
        return "trainingblade", "nightfall"
