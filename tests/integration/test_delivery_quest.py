from services.delievry_minigame_services import (
    create_quest,
    fetch_quest,
    delete_quest,
    items_check,
)


def test_create_quest_creates_db_row(user_a):
    items, reward = create_quest(user_a.user_id)

    assert len(items) in (1, 2)
    assert reward > 0

    quest = fetch_quest(user_a.user_id)
    assert quest is not None

def test_delete_quest_increments_skip(user_b):
    create_quest(user_b.user_id)
    success = delete_quest(user_b.user_id)
    assert success is True

    quest = fetch_quest(user_b.user_id)
    assert quest.delivery_items is None

def test_items_check_success(user_a):
    create_quest(user_a.user_id)
    quest = fetch_quest(user_a.user_id)

    result = items_check(user_a.user_id, quest.delivery_items)
    assert result is True

    quest = fetch_quest(user_a.user_id)
    assert quest.streak == 1