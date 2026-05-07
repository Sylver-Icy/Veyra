import asyncio

from services.battle.battle_view import BattleRoundView, NO_SPELL_EQUIPPED_MESSAGE


class FakeResponse:
    def __init__(self):
        self.messages = []

    async def send_message(self, content, **kwargs):
        self.messages.append((content, kwargs))


class FakeInteraction:
    def __init__(self, user_id):
        self.user = type("User", (), {"id": user_id})()
        self.response = FakeResponse()


def test_no_spell_cast_click_sends_ephemeral_error_without_locking_move():
    async def run_click():
        view = BattleRoundView(1, 2, spellless_user_ids={1})
        interaction = FakeInteraction(1)
        await view._handle_move(interaction, "cast")
        return view, interaction

    view, interaction = asyncio.run(run_click())

    assert interaction.response.messages == [
        (NO_SPELL_EQUIPPED_MESSAGE, {"ephemeral": True})
    ]
    assert view.moves == {}


def test_spell_user_cast_click_still_locks_move():
    async def run_click():
        view = BattleRoundView(1, 2, spellless_user_ids=set())
        interaction = FakeInteraction(1)
        await view._handle_move(interaction, "cast")
        return view

    view = asyncio.run(run_click())

    assert view.moves == {1: "cast"}
