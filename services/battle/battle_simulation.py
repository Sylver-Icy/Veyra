# services/discord_battle/battle_simulation.py
import asyncio
import discord
from services.battle.battle_class import Battle
from services.battle.battlemanager_class import BattleManager
from services.battle.spell_class import Fireball, Heavyshot, ErdtreeBlessing, Nightfall, FrostBite

from services.battle.battle_view import BattleRoundView
from services.economy_services import add_gold
from utils.embeds.battleembed import (
    build_round_embed,
    build_result_embed,
    build_final_embed,
)

TIMEOUT_SECONDS = 50
TIMEOUT_PENALTY = 25
RESULT_DISPLAY_TIME = 12  # seconds before next round starts
async def start_battle_simulation(ctx, challenger: discord.User, target: discord.User, bet: int):
    """
    Orchestrates a full 1v1 battle flow in-channel.
    - New embed each round (previous deleted).
    - Auto-advance when both moves are locked.
    - 50s timeout => -25 HP penalty to the late player(s).
    - Ends immediately on death; announces winner and reward.
    """
    # Initialize fighters from usernames
    p1 = Battle(challenger.name, Nightfall())
    p2 = Battle(target.name, ErdtreeBlessing())
    bm = BattleManager(p1, p2)

    round_num = 1
    # Initial round announce
    round_embed = build_round_embed(round_num, p1, p2, challenger.name, target.name)
    view = BattleRoundView(p1_id=challenger.id, p2_id=target.id, timeout=TIMEOUT_SECONDS)
    cur_message = await ctx.channel.send(embed=round_embed, view=view)

    try:
        while True:
            # Wait for both moves or timeout
            try:
                await asyncio.wait_for(view.wait(), timeout=TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                # View might not have stopped;  handle penalties below
                pass

            # Determine selections and timeouts
            p1_move = view.moves.get(challenger.id)
            p2_move = view.moves.get(target.id)
            p1_timed_out = p1_move is None
            p2_timed_out = p2_move is None

            # Default any missing move to "attack" so the engine can still resolve the round
            if p1_move is None:
                p1_move = "attack"
            if p2_move is None:
                p2_move = "attack"

            # Execute + resolve the round via  ngine
            bm.execute_turn(p1_move, p2_move)
            result_text = bm.resolve_round()


            # Apply timeout penalties AFTER resolution
            penalty_notes = []

            if p1_timed_out:
                p1.hp = max(0, p1.hp - TIMEOUT_PENALTY)
                penalty_notes.append(f"{challenger.name} suffered an extra **-{TIMEOUT_PENALTY} HP** for hesitation.")
            if p2_timed_out:
                p2.hp = max(0, p2.hp - TIMEOUT_PENALTY)
                penalty_notes.append(f"{target.name} suffered an extra **-{TIMEOUT_PENALTY} HP** for hesitation.")

            # Trigger all  effects each round

            p1_penalty_notes = p1.proc_effect()
            p2_penalty_notes = p2.proc_effect()
            penalty_notes = (p1_penalty_notes or []) + (p2_penalty_notes or [])



            # Replace the old round message with the result message
            result_embed = build_result_embed(
                round_num,
                challenger.name, target.name,
                p1_move, p2_move,
                result_text + (("\n" + "\n".join(penalty_notes)) if penalty_notes else ""),
                p1_timed_out, p2_timed_out
            )

            result_msg = await ctx.channel.send(embed=result_embed)

            # Delete the previous round's input embed immediately (we don’t need it anymore)
            with contextlib_silent():
                await cur_message.delete()

            # 🕒 Give players time to read the result before next round
            await asyncio.sleep(RESULT_DISPLAY_TIME)

            # Check for battle end conditions after displaying result
            if p1.hp <= 0 and p2.hp <= 0:
                final_embed = build_final_embed(None, None, bet, both_dead=True)
                await ctx.channel.send(embed=final_embed)
                return
            elif p1.hp <= 0:
                #P2 won give reward
                add_gold(target.id, int((bet * 2) * 0.9))
                final_embed = build_final_embed(target.name, challenger.name, bet)
                await ctx.channel.send(embed=final_embed)
                return
            elif p2.hp <= 0:
                add_gold(challenger.id, int((bet * 2) * 0.9))
                final_embed = build_final_embed(challenger.name, target.name, bet)
                await ctx.channel.send(embed=final_embed)
                return

            # Prepare for next round
            round_num += 1
            next_round_embed = build_round_embed(round_num, p1, p2, challenger.name, target.name)
            view = BattleRoundView(p1_id=challenger.id, p2_id=target.id, timeout=TIMEOUT_SECONDS)
            cur_message = await ctx.channel.send(embed=next_round_embed, view=view)

            # Now delete the result message to keep things clean
            with contextlib_silent():
                await result_msg.delete()

    finally:
        # Best-effort cleanup of any dangling views/messages
        try:
            if cur_message:
                await cur_message.edit(view=None)
        except Exception:
            pass


# ---- tiny helper: suppress deletes when already deleted ----
from contextlib import contextmanager

@contextmanager
def contextlib_silent():
    try:
        yield
    except Exception:
        pass