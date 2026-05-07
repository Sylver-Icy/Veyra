from database.seed_data import ITEMS
from domain.battle.gear_shards import (
    GEAR_SHARDS,
    GEAR_TYPE_SPELL,
    GEAR_TYPE_WEAPON,
    account_bound_shard_item_ids,
    droppable_shard_item_ids,
    get_shard_by_item_id,
    non_droppable_shard_item_ids,
)
from services.battle.content_registry import CONTENT_REGISTRY


def test_every_registered_weapon_and_spell_has_shard_metadata():
    shard_keys = {(shard.gear_type, shard.gear_key) for shard in GEAR_SHARDS}

    assert {
        (GEAR_TYPE_WEAPON, weapon_key)
        for weapon_key in CONTENT_REGISTRY.list_weapons()
    }.issubset(shard_keys)
    assert {
        (GEAR_TYPE_SPELL, spell_key)
        for spell_key in CONTENT_REGISTRY.list_spells()
    }.issubset(shard_keys)


def test_every_shard_has_seeded_item_row_and_unique_id():
    item_ids = [item["item_id"] for item in ITEMS]
    seeded_ids = set(item_ids)

    assert len(item_ids) == len(seeded_ids)
    for shard in GEAR_SHARDS:
        assert shard.item_id in seeded_ids


def test_shard_ids_are_reserved_in_catalog_order():
    assert [shard.item_id for shard in GEAR_SHARDS] == list(range(3001, 3015))


def test_mythic_shards_are_account_bound_and_not_droppable():
    mythic_shards = [shard for shard in GEAR_SHARDS if shard.rarity == "Mythic"]

    assert {shard.item_id for shard in mythic_shards} == account_bound_shard_item_ids()
    assert all(shard.account_bound for shard in mythic_shards)
    assert all(not shard.drop_pool for shard in mythic_shards)
    assert account_bound_shard_item_ids().isdisjoint(droppable_shard_item_ids())


def test_boxes_can_drop_normal_shards_but_never_mythic_or_starter_shards():
    droppable_ids = droppable_shard_item_ids()
    blocked_ids = non_droppable_shard_item_ids()

    assert get_shard_by_item_id(3002).item_id in droppable_ids
    assert get_shard_by_item_id(3008).item_id in droppable_ids
    assert 3001 in blocked_ids
    assert 3006 in blocked_ids
    assert 3007 in blocked_ids
