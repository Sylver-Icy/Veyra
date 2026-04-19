
"""
Central battle rules & definitions.
Contains allowed weapons, spells, and helper accessors.
"""

from services.battle.content_registry import CONTENT_REGISTRY


def get_allowed_weapons():
    """Return list of weapon keys."""
    return CONTENT_REGISTRY.list_weapons()


def get_allowed_spells():
    """Return list of spell keys."""
    return CONTENT_REGISTRY.list_spells()


def get_weapon_label(weapon_key: str) -> str:
    """Return display label for weapon."""
    weapon = CONTENT_REGISTRY.get_weapon(weapon_key)
    return weapon.label if weapon else weapon_key


def get_spell_label(spell_key: str) -> str:
    """Return display label for spell."""
    spell = CONTENT_REGISTRY.get_spell(spell_key)
    return spell.label if spell else spell_key


def get_weapon_unlock_stage(weapon_key: str) -> int:
    weapon = CONTENT_REGISTRY.get_weapon(weapon_key)
    return weapon.unlock_stage if weapon else 0


def get_spell_unlock_stage(spell_key: str) -> int:
    spell = CONTENT_REGISTRY.get_spell(spell_key)
    return spell.unlock_stage if spell else 0

def queue_bet_validation(min_bet: int, max_bet: int) -> bool:

    if not isinstance(min_bet, int) or not isinstance(max_bet, int):
        return False

    if min_bet < 1:
        return False

    if max_bet < min_bet:
        return False

    return True
