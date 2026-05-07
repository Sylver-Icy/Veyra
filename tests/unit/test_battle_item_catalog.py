from database.seed_data import ITEMS
from domain.inventory.rules import allowed_stack_size


def item_row(item_id: int) -> dict:
    return next(item for item in ITEMS if item["item_id"] == item_id)


def test_seeded_items_have_split_type_and_rarity_columns():
    allowed_types = {"item", "lootbox", "mineral", "potion", "shard"}
    allowed_rarities = {"Common", "Rare", "Epic", "Legendary", "Mythic"}

    assert all(item["item_type"] in allowed_types for item in ITEMS)
    assert all(item["item_rarity"] in allowed_rarities for item in ITEMS)


def test_special_item_groups_have_domain_types_and_real_rarity():
    assert item_row(176)["item_type"] == "lootbox"
    assert item_row(176)["item_rarity"] == "Common"
    assert item_row(179)["item_type"] == "lootbox"
    assert item_row(179)["item_rarity"] == "Legendary"

    assert item_row(184)["item_type"] == "mineral"
    assert item_row(184)["item_rarity"] == "Common"
    assert item_row(186)["item_type"] == "mineral"
    assert item_row(186)["item_rarity"] == "Epic"

    assert item_row(192)["item_type"] == "potion"
    assert item_row(192)["item_rarity"] == "Common"
    assert item_row(197)["item_type"] == "potion"
    assert item_row(197)["item_rarity"] == "Epic"

    assert item_row(3002)["item_type"] == "shard"
    assert item_row(3002)["item_rarity"] == "Legendary"


def test_stack_limits_depend_on_item_type_not_rarity():
    assert allowed_stack_size(1, "item") == 10
    assert allowed_stack_size(1, "mineral") == 20
    assert allowed_stack_size(1, "lootbox") == 2
    assert allowed_stack_size(1, "shard") == 50
    assert allowed_stack_size(1, "legendary") == 0
