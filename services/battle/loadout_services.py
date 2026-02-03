"""
Handles weapon/spell loadout updates & retrieval for battle system.
Includes validation for allowed weapons/spells, creates loadouts for new users,
and updates existing entries. Uses SQLAlchemy sessions.
"""

from database.sessionmaker import Session

from models.users_model import BattleLoadout

from services.battle.campaign.campaign_services import get_campaign_stage


# Allowed weapons players can equip (alpha set)
allowed_weapons = ("elephanthammer", "moonslasher", "trainingblade", "eternaltome", "veyrasgrimoire", "darkblade", "bardoksclaymore")

# Allowed spells players can equip (alpha set)
allowed_spells = ("fireball", "nightfall", "heavyshot", "erdtreeblessing", "frostbite", "veilofdarkness", "earthquake")

def _normalize_input(value: str) -> str:
    """
    Normalize user input for weapons/spells.
    - lowercase
    - remove spaces and underscores
    """
    return value.lower().replace(" ", "").replace("_", "")

def update_loadout(user_id: int, weapon: str, spell: str):
    """
    Update or create a player's battle loadout.

    - Validates weapon/spell names
    - Updates existing loadout if present
    - Creates a new loadout row if user has none
    Returns a status message for the user.
    """
    weapon_key = _normalize_input(weapon)
    spell_key = _normalize_input(spell)
    
    # Validate user input before touching the database
    if weapon_key not in allowed_weapons:
        return f"{weapon} is incorrect pick among {allowed_weapons}"

    if spell_key not in allowed_spells:
        return f"{spell} bruh what kinda incantations you tryna do ?? pick from {allowed_spells}"

    if spell_key == "veilofdarkness":
        if get_campaign_stage(user_id) < 10:
            return "*Veil of Darkness* is a campaign spell. Reach campaign stage 10 to unlock it!"

    if weapon_key == "veyrasgrimoire":
        if get_campaign_stage(user_id) < 10:
            return "*Veyra's Grimoire* is a campaign weapon. Reach campaign stage 10 to unlock it!"

    if weapon_key == "bardoksclaymore":
        if get_campaign_stage(user_id) < 15:
            return "*Bardok's Claymore* is unlocked at campaign stage 15!"

    # Open DB session and fetch existing loadout
    with Session() as session:
        # If user already has a loadout, update it
        warrior = session.get(BattleLoadout, user_id)
        if warrior:
            warrior.weapon = weapon_key
            warrior.spell = spell_key
            session.commit()
            return f"Loadout updated You currently have {weapon} as weapon and your spell is {spell}"

        # If user has no loadout, create a new one
        new_entry = BattleLoadout(
            user_id = user_id,
            weapon = weapon_key,
            spell = spell_key
        )
        session.add(new_entry)
        session.commit()
        return f"You currently have {weapon} as weapon and your spell is {spell}"

def fetch_loadout(user_id: int):
    """
    Fetch the user's equipped weapon & spell.
    Returns default loadout if user has none.
    """
    with Session() as session:
        warrior = session.get(BattleLoadout, user_id)

        if warrior:
            return (warrior.weapon, warrior.spell)

        # Default loadout for new users
        return "trainingblade", "nightfall"