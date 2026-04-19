from services.battle.content_registry import CONTENT_REGISTRY


def test_content_registry_exposes_current_weapon_and_spell_keys():
    assert "trainingblade" in CONTENT_REGISTRY.list_weapons()
    assert "nightfall" in CONTENT_REGISTRY.list_spells()


def test_content_registry_returns_metadata_for_registered_content():
    weapon = CONTENT_REGISTRY.get_weapon("veyrasgrimoire")
    spell = CONTENT_REGISTRY.get_spell("veilofdarkness")
    arena = CONTENT_REGISTRY.get_arena("lava")
    npc = CONTENT_REGISTRY.get_npc("bardok")

    assert weapon.label == "Veyra's Grimoire"
    assert weapon.unlock_stage == 10
    assert spell.label == "Veil of Darkness"
    assert spell.unlock_stage == 10
    assert arena.label == "Lava Arena"
    assert npc.label == "Bardok"


def test_content_registry_creates_content_with_stable_keys():
    weapon = CONTENT_REGISTRY.create_weapon("bardoksclaymore")
    spell = CONTENT_REGISTRY.create_spell("earthquake")

    assert weapon.content_key == "bardoksclaymore"
    assert spell.content_key == "earthquake"


def test_content_registry_can_create_registered_arenas_and_npcs():
    arena = CONTENT_REGISTRY.create_arena("frozen")
    fighter = type("Fighter", (), {"origin": "player"})()
    opponent = type("Opponent", (), {"move_history": []})()
    npc_ai = CONTENT_REGISTRY.create_npc_ai("bardok", fighter=fighter, opponent=opponent, stage=13)

    assert arena.__class__.__name__ == "FrozenArena"
    assert npc_ai.__class__.__name__ == "BardokAI"

