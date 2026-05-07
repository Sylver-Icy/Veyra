from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass
from typing import Callable

import discord

from services.battle.battle_class import Battle
from services.battle.battle_view import TutorialBattleRoundView
from services.battle.battlemanager_class import BattleManager
from services.battle.content_registry import CONTENT_REGISTRY
from services.battle.session_runner import BattleSession
from services.battle.spell_class import Fireball


VEYRA_TUTORIAL_ID = 1
TIMEOUT_SECONDS = 50
TUTORIAL_LOCKED_MODE = "tutorial"
TUTORIAL_RESTART_MESSAGE = "Restarting your starter duel."
TUTORIAL_BUSY_MESSAGE = "Finish your current battle first."
TUTORIAL_TIMEOUT_MESSAGE = "Focus. Press **{move}** to continue."
TUTORIAL_FINAL_MESSAGE = "Well, you're a good fighter ig. We can be frnds. Lemme show you what else you can do in Natlade."

ACTIVE_TUTORIAL_TOKENS: dict[int, object] = {}
ACTIVE_TUTORIAL_VIEWS: dict[int, TutorialBattleRoundView] = {}


def _active_battles():
    from services.battle.battle_simulation import ACTIVE_BATTLES

    return ACTIVE_BATTLES


@dataclass(frozen=True)
class TutorialStep:
    round_number: int
    required_move: str
    required_label: str
    veyra_move: str
    prompt: str
    after_line: str
    setup: Callable[[BattleSession], None] | None = None


def _setup_cast_lesson(session: BattleSession) -> None:
    session.p1.mana = max(session.p1.mana, 15)
    session.p2.hp = min(session.p2.hp, 16)


TUTORIAL_STEPS = (
    TutorialStep(
        round_number=1,
        required_move="attack",
        required_label="Attack",
        veyra_move="recover",
        prompt="Press **Attack**. It does damage and blocks Recover if enemy tries it.",
        after_line="Good. Attack cuts off Recover. It's damage scales with your attack stat and enemy defense stat.",
    ),
    TutorialStep(
        round_number=2,
        required_move="block",
        required_label="Block",
        veyra_move="attack",
        prompt="Now press **Block**. If you read Attack, you can block it and save HP.",
        after_line="See? Block makes you take less damage from Attack and you get defense stat for correct prediction.",
    ),
    TutorialStep(
        round_number=3,
        required_move="counter",
        required_label="Counter",
        veyra_move="attack",
        prompt="Press **Counter**. This only works if you read Attack. Deflect 50% damage back",
        after_line="Clean. Use counter only if you read Attack. Miss it and you loose stats",
    ),
    TutorialStep(
        round_number=4,
        required_move="recover",
        required_label="Recover",
        veyra_move="block",
        prompt="Press **Recover**. Use it when enemy plays safe.",
        after_line="Good. Recover buys HP or Mana. Just make sure to use when enemy is not attacking.",
    ),
    TutorialStep(
        round_number=5,
        required_move="cast",
        required_label="Cast",
        veyra_move="counter",
        prompt="Last one: press **Cast**. It uses your equipped spell. Spells have different effects and mana costs.",
        after_line="That was outstanding. Cast is the most powerful move, but it requires mana and you can only have one spell equipped. This one was a fireball that does damage, but there are many more to discover.",
        setup=_setup_cast_lesson,
    ),
)


def _is_current_tutorial(user_id: int, token: object) -> bool:
    return ACTIVE_TUTORIAL_TOKENS.get(user_id) is token


def _build_tutorial_session(player_name: str) -> BattleSession:
    player = Battle(
        player_name,
        Fireball(),
        CONTENT_REGISTRY.create_weapon("trainingblade"),
    )
    veyra = Battle(
        "Veyra",
        Fireball(),
        CONTENT_REGISTRY.create_weapon("trainingblade"),
    )
    return BattleSession(BattleManager(player, veyra), timeout_penalty=0)


def build_tutorial_final_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Welcome to Natlade",
        description="Pick a path. Or press everything and learn the hard way.",
        color=discord.Color.blurple(),
    )
    embed.add_field(
        name="Fight",
        value="`/battle @user <bet>` - duel for gold\n`/open_to_battle` - queue up\n`/campaign` - solo fights",
        inline=False,
    )
    embed.add_field(
        name="Gear",
        value="`/loadout` - equip weapons/spells\nOpen boxes for shards and unlock stronger toys.",
        inline=False,
    )
    embed.add_field(
        name="Earn",
        value="`/work knight` - quick gold\n`/work miner` or `/work digger` - resources and boxes",
        inline=False,
    )
    embed.add_field(
        name="Gamble",
        value="`/casino` - buy/cashout chips\n`/gamble slots` - spin if your wallet can handle it",
        inline=False,
    )
    embed.add_field(
        name="Need directions?",
        value="`/help` for commands\n`/details battle`, `/details loadout`, `/details gambling` for guides",
        inline=False,
    )
    embed.set_footer(text="Veyra • Start with /campaign if you want to practice more or earn some gold before dueling others. or just jump into PvP with /battle @user")
    return embed


def _prepare_tutorial_round(session: BattleSession, step: TutorialStep) -> None:
    if step.setup:
        step.setup(session)


def _resolve_tutorial_step(session: BattleSession, step: TutorialStep):
    _prepare_tutorial_round(session, step)
    return session.process_round(
        round_number=step.round_number,
        p1_move=step.required_move,
        p2_move=step.veyra_move,
        p1_timed_out=False,
        p2_timed_out=False,
        p1_name=session.p1.name,
        p2_name=session.p2.name,
    )


async def start_tutorial_battle(ctx, player, round_pause: float = 1.0):
    from services.tutorial_services import TutorialState, advance
    from utils.embeds.battleembed import build_result_embed, build_round_embed

    active_battles = _active_battles()
    active_mode = active_battles.get(player.id)
    if active_mode and active_mode != TUTORIAL_LOCKED_MODE:
        await ctx.send(TUTORIAL_BUSY_MESSAGE)
        return

    old_view = ACTIVE_TUTORIAL_VIEWS.pop(player.id, None)
    if old_view:
        old_view.stop()
        await ctx.send(TUTORIAL_RESTART_MESSAGE)

    token = object()
    ACTIVE_TUTORIAL_TOKENS[player.id] = token
    active_battles[player.id] = TUTORIAL_LOCKED_MODE
    await advance(player.id, TutorialState.IN_TUTORIAL_BATTLE)

    session = _build_tutorial_session(player.name)

    try:
        for step in TUTORIAL_STEPS:
            while _is_current_tutorial(player.id, token):
                _prepare_tutorial_round(session, step)
                view = TutorialBattleRoundView(
                    player_id=player.id,
                    veyra_id=VEYRA_TUTORIAL_ID,
                    required_move=step.required_move,
                    veyra_move=step.veyra_move,
                    required_label=step.required_label,
                    timeout=TIMEOUT_SECONDS,
                )
                ACTIVE_TUTORIAL_VIEWS[player.id] = view
                round_message = await ctx.channel.send(
                    content=step.prompt,
                    embed=build_round_embed(
                        step.round_number,
                        session.p1,
                        session.p2,
                        player.name,
                        "Veyra",
                    ),
                    view=view,
                )

                try:
                    await asyncio.wait_for(view.wait(), timeout=TIMEOUT_SECONDS)
                except asyncio.TimeoutError:
                    pass

                if not _is_current_tutorial(player.id, token):
                    return

                if view.moves.get(player.id) != step.required_move:
                    with suppress(Exception):
                        await round_message.edit(view=None)
                    await ctx.channel.send(TUTORIAL_TIMEOUT_MESSAGE.format(move=step.required_label))
                    continue

                with suppress(Exception):
                    await round_message.edit(view=view)

                outcome = session.process_round(
                    round_number=step.round_number,
                    p1_move=step.required_move,
                    p2_move=step.veyra_move,
                    p1_timed_out=False,
                    p2_timed_out=False,
                    p1_name=player.name,
                    p2_name="Veyra",
                )
                await ctx.channel.send(
                    content=f"Veyra: {step.after_line}",
                    embed=build_result_embed(
                        step.round_number,
                        player.name,
                        "Veyra",
                        outcome.p1_move,
                        outcome.p2_move,
                        outcome.result_text,
                        outcome.p1_timed_out,
                        outcome.p2_timed_out,
                    ),
                )
                await asyncio.sleep(round_pause)
                break

        if _is_current_tutorial(player.id, token):
            session.p2.hp = 0
            await advance(player.id, TutorialState.COMPLETED)
            await ctx.channel.send(TUTORIAL_FINAL_MESSAGE, embed=build_tutorial_final_embed())
    finally:
        if _is_current_tutorial(player.id, token):
            ACTIVE_TUTORIAL_TOKENS.pop(player.id, None)
            ACTIVE_TUTORIAL_VIEWS.pop(player.id, None)
            active_battles.pop(player.id, None)
