from domain.battle.rules import (
    get_allowed_spells,
    get_allowed_weapons,
    get_spell_label,
    get_spell_unlock_stage,
    get_weapon_label,
    get_weapon_unlock_stage,
    queue_bet_validation,
)


def test_allowed_battle_content_contains_expected_defaults():
    assert "trainingblade" in get_allowed_weapons()
    assert "veyrasgrimoire" in get_allowed_weapons()
    assert "fireball" in get_allowed_spells()
    assert "veilofdarkness" in get_allowed_spells()


def test_battle_labels_and_unlock_stages_use_rule_tables():
    assert get_weapon_label("trainingblade") == "Training Blade"
    assert get_weapon_unlock_stage("veyrasgrimoire") == 10
    assert get_spell_label("veilofdarkness") == "Veil of Darkness"
    assert get_spell_unlock_stage("veilofdarkness") == 10


def test_unknown_labels_fall_back_to_raw_key():
    assert get_weapon_label("mysteryblade") == "mysteryblade"
    assert get_spell_label("mysteryspell") == "mysteryspell"


def test_queue_bet_validation_accepts_valid_ranges():
    assert queue_bet_validation(10, 100) is True


def test_queue_bet_validation_rejects_bad_ranges():
    assert queue_bet_validation("10", 100) is False
    assert queue_bet_validation(0, 100) is False
    assert queue_bet_validation(100, 10) is False
