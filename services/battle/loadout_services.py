"""
Handles weapon/spell loadout updates & retrieval for battle system.
Includes validation for allowed weapons/spells, creates loadouts for new users,
and updates existing entries. Uses SQLAlchemy sessions.
"""

from database.sessionmaker import Session

from models.users_model import BattleLoadout


# Allowed weapons players can equip (alpha set)
allowed_weapons = ("elephanthammer", "moonslasher", "trainingblade", "eternaltome", "darkblade")

# Allowed spells players can equip (alpha set)
allowed_spells = ("fireball", "nightfall", "heavyshot", "erdtreeblessing", "frostbite")

def update_loadout(user_id: int, weapon: str, spell: str):
    """
    Update or create a player's battle loadout.

    - Validates weapon/spell names
    - Updates existing loadout if present
    - Creates a new loadout row if user has none
    Returns a status message for the user.
    """
    # Validate user input before touching the database
    if weapon.lower() not in allowed_weapons:
        return f"{weapon} is incorrect pick among {allowed_weapons}"

    if spell.lower() not in allowed_spells:
        return f"{spell} bruh what kinda incantations you tryna do ?? pick from {allowed_spells}"

    # Open DB session and fetch existing loadout
    with Session() as session:
        # If user already has a loadout, update it
        warrior = session.get(BattleLoadout, user_id)
        if warrior:
            warrior.weapon = weapon.lower()
            warrior.spell = spell.lower()
            session.commit()
            return f"Loadout updated You currently have {weapon} as weapon and your spell is {spell}"

        # If user has no loadout, create a new one
        new_entry = BattleLoadout(
            user_id = user_id,
            weapon = weapon.lower(),
            spell = spell.lower()
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