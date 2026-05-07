"""Inventory-backed ownership helpers for battle gear shards."""

from database.sessionmaker import Session
from domain.battle.gear_shards import (
    GearShardDefinition,
    get_spell_shard,
    get_weapon_shard,
    starter_weapon_shard,
)
from models.inventory_model import Inventory


def _owns_shard(user_id: int, shard: GearShardDefinition | None, session) -> bool:
    if shard is None:
        return False

    entry = session.get(Inventory, (user_id, shard.item_id))
    return bool(entry and entry.item_quantity >= 1)


def owns_weapon(user_id: int, weapon_key: str, session=None) -> bool:
    owns_session = session is None
    if owns_session:
        session = Session()

    try:
        return _owns_shard(user_id, get_weapon_shard(weapon_key), session)
    finally:
        if owns_session:
            session.close()


def owns_spell(user_id: int, spell_key: str | None, session=None) -> bool:
    if not spell_key:
        return False

    owns_session = session is None
    if owns_session:
        session = Session()

    try:
        return _owns_shard(user_id, get_spell_shard(spell_key), session)
    finally:
        if owns_session:
            session.close()


def grant_starter_weapon_shard(user_id: int, session) -> None:
    """Grant the free Training Blade unlock inside an existing user transaction."""
    shard = starter_weapon_shard()
    entry = session.get(Inventory, (user_id, shard.item_id))

    if entry:
        entry.item_quantity += 1
        return

    session.add(
        Inventory(
            user_id=user_id,
            item_id=shard.item_id,
            item_quantity=1,
        )
    )
