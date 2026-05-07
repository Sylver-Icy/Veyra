import asyncio

from services import tutorial_services
from services.battle.battle_view import TutorialBattleRoundView
from services.battle import tutorial_battle_services


class FakeResponse:
    def __init__(self):
        self.messages = []

    async def send_message(self, content, **kwargs):
        self.messages.append((content, kwargs))


class FakeInteraction:
    def __init__(self, user_id):
        self.user = type("User", (), {"id": user_id})()
        self.response = FakeResponse()


class FakeCtx:
    def __init__(self):
        self.author = type("Author", (), {"id": 123})()
        self.messages = []

    async def send(self, content=None, **kwargs):
        self.messages.append((content, kwargs))


def test_tutorial_wrong_move_sends_ephemeral_error_without_locking():
    async def run_click():
        view = TutorialBattleRoundView(
            player_id=1,
            veyra_id=99,
            required_move="attack",
            veyra_move="recover",
            required_label="Attack",
        )
        interaction = FakeInteraction(1)
        await view._handle_player_move(interaction, "block")
        return view, interaction

    view, interaction = asyncio.run(run_click())

    assert interaction.response.messages == [
        ("Not yet. You're learning rn; experiment later. Press **Attack**.", {"ephemeral": True})
    ]
    assert view.moves == {}


def test_tutorial_correct_move_locks_both_moves_and_disables_buttons():
    async def run_click():
        view = TutorialBattleRoundView(
            player_id=1,
            veyra_id=99,
            required_move="attack",
            veyra_move="recover",
            required_label="Attack",
        )
        interaction = FakeInteraction(1)
        await view._handle_player_move(interaction, "attack")
        return view, interaction

    view, interaction = asyncio.run(run_click())

    assert interaction.response.messages == [
        ("Locked **Attack** ✅", {"ephemeral": True})
    ]
    assert view.moves == {1: "attack", 99: "recover"}
    assert all(child.disabled for child in view.children)


def test_tutorial_script_is_five_moves_and_ends_with_user_win():
    session = tutorial_battle_services._build_tutorial_session("Newbie")

    outcomes = [
        tutorial_battle_services._resolve_tutorial_step(session, step)
        for step in tutorial_battle_services.TUTORIAL_STEPS
    ]

    assert len(outcomes) == 5
    assert [step.required_move for step in tutorial_battle_services.TUTORIAL_STEPS] == [
        "attack",
        "block",
        "counter",
        "recover",
        "cast",
    ]
    assert session.p1.hp > 0
    assert session.p2.hp <= 0


def test_tutorial_final_embed_points_to_main_next_steps():
    embed = tutorial_battle_services.build_tutorial_final_embed()

    values = "\n".join(field.value for field in embed.fields)

    assert embed.title == "Welcome to Natlade"
    assert "/battle" in values
    assert "/work knight" in values
    assert "/casino" in values
    assert "/gamble slots" in values
    assert "/help" in values
    assert "/details battle" in values


def test_tutorial_guard_allows_help_details_profile_and_hello(monkeypatch):
    async def fake_state(_user_id):
        return tutorial_services.TutorialState.IN_TUTORIAL_BATTLE

    monkeypatch.setattr(tutorial_services, "get_tutorial_state", fake_state)
    ctx = FakeCtx()

    async def run_checks():
        return [
            await tutorial_services.tutorial_guard(ctx, command, [])
            for command in ("help", "details", "profile", "helloVeyra")
        ]

    assert asyncio.run(run_checks()) == [False, False, False, False]
    assert ctx.messages == []


def test_tutorial_guard_blocks_other_commands_while_in_tutorial(monkeypatch):
    async def fake_state(_user_id):
        return tutorial_services.TutorialState.IN_TUTORIAL_BATTLE

    monkeypatch.setattr(tutorial_services, "get_tutorial_state", fake_state)
    ctx = FakeCtx()

    blocked = asyncio.run(tutorial_services.tutorial_guard(ctx, "battle", []))

    assert blocked is True
    assert ctx.messages == [
        (tutorial_services.TUTORIAL_BLOCK_MESSAGE, {})
    ]


def test_completed_tutorial_does_not_block_commands(monkeypatch):
    async def fake_state(_user_id):
        return tutorial_services.TutorialState.COMPLETED

    monkeypatch.setattr(tutorial_services, "get_tutorial_state", fake_state)
    ctx = FakeCtx()

    blocked = asyncio.run(tutorial_services.tutorial_guard(ctx, "battle", []))

    assert blocked is False
    assert ctx.messages == []
