import pytest
from domain.quest.rules import (
    allowed_rarities_for_level,
    number_of_items_for_quest,
    base_reward_for_rarities,
    streak_multiplier,
    can_skip,
)

def test_allowed_rarities_boundaries():
    assert allowed_rarities_for_level(1) == ["Common"]
    assert allowed_rarities_for_level(5) == ["Common", "Rare"]
    assert "Epic" in allowed_rarities_for_level(14)

def test_number_of_items_range():
    for _ in range(50):
        assert number_of_items_for_quest() in (1, 2)

def test_base_reward_common():
    reward = base_reward_for_rarities(["Common"])
    assert 10 <= reward <= 15

def test_streak_multiplier_curve():
    assert streak_multiplier(0) == 1.0
    assert streak_multiplier(3) == 1.2
    assert streak_multiplier(7) == 1.5
    assert streak_multiplier(15) == 2.0

def test_can_skip_limit():
    assert can_skip(2) is True
    assert can_skip(3) is False