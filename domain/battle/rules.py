

"""
Central battle rules & definitions.
Contains allowed weapons, spells, and helper accessors.
"""

# ===== WEAPONS =====
WEAPONS = {
    "trainingblade": {
        "label": "Training Blade",
        "unlock_stage": 0,
    },
    "elephanthammer": {
        "label": "Elephant Hammer",
        "unlock_stage": 0,
    },
    "moonslasher": {
        "label": "Moon Slasher",
        "unlock_stage": 0,
    },
    "veyrasgrimoire": {
        "label": "Veyra's Grimoire",
        "unlock_stage": 10,
    },
    "bardoksclaymore": {
        "label": "Bardok's Claymore",
        "unlock_stage": 15,
    },
}


# ===== SPELLS =====
SPELLS = {
    "nightfall": {
        "label": "Nightfall",
        "unlock_stage": 0,
    },
    "fireball": {
        "label": "Fireball",
        "unlock_stage": 0,
    },
    "frostbite": {
        "label": "Frostbite",
        "unlock_stage": 0,
    },
    "veilofdarkness": {
        "label": "Veil of Darkness",
        "unlock_stage": 10,
    },
}


# ===== ACCESSORS =====

def get_allowed_weapons():
    """Return list of weapon keys."""
    return list(WEAPONS.keys())


def get_allowed_spells():
    """Return list of spell keys."""
    return list(SPELLS.keys())


def get_weapon_label(weapon_key: str) -> str:
    """Return display label for weapon."""
    return WEAPONS.get(weapon_key, {}).get("label", weapon_key)


def get_spell_label(spell_key: str) -> str:
    """Return display label for spell."""
    return SPELLS.get(spell_key, {}).get("label", spell_key)


def get_weapon_unlock_stage(weapon_key: str) -> int:
    return WEAPONS.get(weapon_key, {}).get("unlock_stage", 0)


def get_spell_unlock_stage(spell_key: str) -> int:
    return SPELLS.get(spell_key, {}).get("unlock_stage", 0)