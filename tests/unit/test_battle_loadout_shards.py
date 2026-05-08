import sys
import types

sessionmaker_stub = types.ModuleType("database.sessionmaker")
sessionmaker_stub.Session = lambda: None
sys.modules["database.sessionmaker"] = sessionmaker_stub

from services.battle import loadout_services


class FakeSession:
    def __init__(self, warrior=None):
        self.warrior = warrior
        self.added = None
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def get(self, model, key):
        return self.warrior

    def add(self, obj):
        self.added = obj

    def commit(self):
        self.committed = True


def test_zero_weapon_shards_cannot_equip(monkeypatch):
    monkeypatch.setattr(loadout_services, "owns_weapon", lambda *_args: False)

    result = loadout_services.update_loadout(123, weapon="darkblade")

    assert result["success"] is False
    assert "Dark Blade" in result["message"]
    assert "Dark Blade Shard" not in result["message"]


def test_one_weapon_shard_can_equip(monkeypatch):
    fake_session = FakeSession()
    monkeypatch.setattr(loadout_services, "Session", lambda: fake_session)
    monkeypatch.setattr(loadout_services, "owns_weapon", lambda *_args: True)

    result = loadout_services.update_loadout(123, weapon="darkblade")

    assert result["success"] is True
    assert result["weapon"] == "darkblade"
    assert result["spell"] is None
    assert fake_session.committed is True


def test_zero_spell_shards_cannot_equip(monkeypatch):
    monkeypatch.setattr(loadout_services, "owns_spell", lambda *_args: False)

    result = loadout_services.update_loadout(123, spell="fireball")

    assert result["success"] is False
    assert "Fireball" in result["message"]
    assert "Fireball Shard" not in result["message"]


def test_fetch_loadout_falls_back_to_training_blade_and_no_spell(monkeypatch):
    warrior = type("Warrior", (), {"weapon": "darkblade", "spell": "fireball"})()
    fake_session = FakeSession(warrior)
    monkeypatch.setattr(loadout_services, "Session", lambda: fake_session)
    monkeypatch.setattr(loadout_services, "owns_weapon", lambda *_args: False)
    monkeypatch.setattr(loadout_services, "owns_spell", lambda *_args: False)

    assert loadout_services.fetch_loadout(123) == ("trainingblade", None)
