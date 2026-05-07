"""
Handles weapon/spell loadout updates & retrieval for battle system.
Includes validation for allowed weapons/spells, creates loadouts for new users,
and updates existing entries. Uses SQLAlchemy sessions.
"""

from database.sessionmaker import Session

from models.users_model import BattleLoadout

from domain.battle.gear_shards import STARTER_WEAPON_KEY

from domain.battle.rules import (
    get_allowed_weapons,
    get_allowed_spells,
    get_weapon_label,
    get_spell_label,
)
from services.battle.gear_shard_services import owns_spell, owns_weapon

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

    if weapon_key and not owns_weapon(user_id, weapon_key):
        return {
            "success": False,
            "message": f"You need 1x {get_weapon_label(weapon_key)} Shard to equip this weapon."
        }

    if spell_key and not owns_spell(user_id, spell_key):
        return {
            "success": False,
            "message": f"You need 1x {get_spell_label(spell_key)} Shard to equip this spell."
        }

    with Session() as session:
        warrior = session.get(BattleLoadout, user_id)

        if warrior:
            if weapon_key:
                warrior.weapon = weapon_key
            if spell_key:
                warrior.spell = spell_key

            session.commit()

            weapon, equipped_spell = fetch_loadout(user_id)
            return {
                "success": True,
                "weapon": weapon,
                "spell": equipped_spell,
                "message": "Loadout updated"
            }

        # Create new loadout. Training Blade is the only free starter gear.
        new_entry = BattleLoadout(
            user_id=user_id,
            weapon=weapon_key or STARTER_WEAPON_KEY,
            spell=spell_key
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
            weapon = warrior.weapon
            if (
                not weapon
                or weapon not in get_allowed_weapons()
                or (weapon != STARTER_WEAPON_KEY and not owns_weapon(user_id, weapon, session))
            ):
                weapon = STARTER_WEAPON_KEY

            spell = warrior.spell
            if not spell or spell not in get_allowed_spells() or not owns_spell(user_id, spell, session):
                spell = None

            return weapon, spell

        return STARTER_WEAPON_KEY, None
