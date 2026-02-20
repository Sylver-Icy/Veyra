import random
from sqlalchemy import select, and_, func

from database.sessionmaker import Session

from models.users_model import BattleQueue

from domain.battle.rules import queue_bet_validation

from services.economy_services import check_wallet_full, remove_gold
from .battle_simulation import start_battle_simulation

from utils.embeds.battleembed import build_match_found_embed, build_removed_from_queue_embed
from utils.custom_errors import NotEnoughGoldError
from utils.embeds.battleembed import send_battle_challenge
from utils.emotes import GOLD_EMOJI
from utils.send_dm import send_dm



def add_to_queue(session, user_id: int, min_bet: int, max_bet: int):

    entry = session.get(BattleQueue, user_id)

    if entry:
        entry.min_bet = min_bet
        entry.max_bet = max_bet
        entry.created_at = func.now()
        return "update"

    new_entry = BattleQueue(
        user_id=user_id,
        min_bet=min_bet,
        max_bet=max_bet
    )

    session.add(new_entry)
    return "add"



def find_match(session, user_id: int, min_bet: int, max_bet: int):
    """
    Find a compatible opponent from the battle queue.

    Matching rules:
    - Exclude the caller
    - Bet ranges must overlap
    - Prefer highest score
    - If score tie -> random choice

    Returns:
        matched_user_id (int) or None
    """

    stmt = (
        select(BattleQueue)
        .where(
            BattleQueue.user_id != user_id,
            BattleQueue.min_bet <= max_bet,
            BattleQueue.max_bet >= min_bet
        )
    )

    candidates = session.execute(stmt).scalars().all()

    if not candidates:
        return None

    # Sort by score descending
    candidates.sort(key=lambda e: e.score, reverse=True)

    top_score = candidates[0].score
    top_candidates = [e for e in candidates if e.score == top_score]

    chosen = random.choice(top_candidates)
    return chosen.user_id



def open_to_battle(user_id: int, min_bet: int, max_bet: int):
    """
    Flow:
    1. Create session
    2. Try to find match
    3. If match -> compute bet based on overlap and return both users
    4. If no match -> add user to queue

    Returns:
        (user_id, opponent_id, bet) OR (None, None, None)
    """

    with Session() as session:
        # Remove stale queue entry if user re-queues
        delete_from_queue(session, [user_id])
        session.commit()

        opponent_id = find_match(session, user_id, min_bet, max_bet)

        if opponent_id is not None:
            opponent_entry = session.get(BattleQueue, opponent_id)

            if not opponent_entry:
                return None, None, None

            overlap_min = max(min_bet, opponent_entry.min_bet)
            overlap_max = min(max_bet, opponent_entry.max_bet)

            if overlap_max < overlap_min:
                return None, None, None

            bet = overlap_max  # max possible within overlap

            delete_from_queue(session, [opponent_id])
            session.commit()

            return user_id, opponent_id, bet

        add_to_queue(session, user_id, min_bet, max_bet)
        session.commit()

        return None, None, None


def delete_from_queue(session, user_ids: list[int]):
    """
    Remove users from the battle queue using an existing session.

    Args:
        session: Active SQLAlchemy session
        user_ids (list[int]): List of user IDs to remove

    Returns:
        int: Number of rows deleted
    """

    if not user_ids:
        return 0

    stmt = (
        select(BattleQueue)
        .where(BattleQueue.user_id.in_(user_ids))
    )

    entries = session.execute(stmt).scalars().all()

    for entry in entries:
        session.delete(entry)

    return len(entries)



async def try_to_start_battle_queue(ctx, user_id: int, min_bet: int, max_bet: int):
    ok = queue_bet_validation(min_bet, max_bet)
    if not ok:
        return "Invalid bet range. Ensure min bet ≥ 1 and max bet ≥ min bet."

    p1_id, p2_id, bet = open_to_battle(user_id, min_bet, max_bet)

    if p2_id is None:
        return f"You are now open to battle ⚔️\nBet range: {min_bet} → {max_bet}{GOLD_EMOJI}\nI’ll DM you when a match is found."

    with Session() as session:
        p1_gold, _ = check_wallet_full(p1_id, session)
        p2_gold, _ = check_wallet_full(p2_id, session)

        if p1_gold < bet:
            return f"You need {bet}{GOLD_EMOJI} to start this battle."

        if p2_gold < bet:
            #remove from q nd dm
            delete_from_queue(session, [p2_id])
            session.commit()
            embed = build_removed_from_queue_embed("Currently not enough gold in wallet. Queue again with smaller bet")
            await send_dm(ctx.bot, p2_id, embed)
            return f"<@{p2_id}> doesn’t have enough gold for this battle."

        embed = build_match_found_embed(p1_id, bet, ctx.channel.id)
        dm_sent = await send_dm(ctx.bot, p2_id, embed)
        if not dm_sent:
            await ctx.respond(f"<@{p2_id}> battle’s ready ⚔️ \nTried to DM you but it didn’t go through. Check your privacy settings or blame Discord.")
        result = await send_battle_challenge(ctx, p1_id, p2_id, bet)

        if result is True:
            try:
                remove_gold(p1_id, bet, session)
                remove_gold(p2_id, bet, session)
                session.commit()

            except NotEnoughGoldError:
                session.rollback()
                return "Gold check failed. Battle cancelled."

            p1_user = await ctx.bot.fetch_user(p1_id)
            p2_user = await ctx.bot.fetch_user(p2_id)
            await start_battle_simulation(ctx, p1_user, p2_user, bet)

            return None

        if result is False:
            return "The challenge was rejected."

        # Timed out / no response: refund pot.
        return "No response received. Match cancelled."
