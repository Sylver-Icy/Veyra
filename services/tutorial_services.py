import asyncio

from discord import ApplicationContext

from enum import IntEnum

from database.sessionmaker import Session
from models.users_model import User


from services.economy_services import check_wallet, add_chip
from services.guessthenumber_services import Guess
from services.shop_services import daily_shop
from services.jobs_services import JobsClass
from services.response_services import create_response

from utils.global_sessions_registry import sessions
from utils.emotes import GOLD_EMOJI



async def safe_send(ctx, content=None, **kwargs):
    if isinstance(ctx, ApplicationContext):
        if not ctx.response.is_done():
            await ctx.respond(content, **kwargs)
        else:
            await ctx.followup.send(content, **kwargs)
    else:
        await ctx.send(content, **kwargs)


class TutorialState(IntEnum):
    NOT_STARTED = 0
    CHECK_WALLET = 1
    PLAY = 2
    OPEN_SHOP = 3
    WORK = 4
    COMPLETED = -1


async def tutorial_completed(user_id: int):
    """
    Returns true if user has already finished tutorial

    :param user_id: Description
    :type user_id: int

    """
    with Session() as session:
        user = session.get(User, user_id)
        if not user: #ts shouldnt even run in first case but checking anyways coz i'm scared T-T
            return False
        return TutorialState(user.tutorial_state) == TutorialState.COMPLETED

async def handle_not_started(ctx, command, arg):
    await safe_send(ctx, "Welcome to Natlade.\nI’ll guide you step by step — don’t rush.\n\nFirst task: check how much gold you have.\nType `!check wallet`")
    await advance(ctx.author.id, TutorialState.CHECK_WALLET)
    return True

async def handle_check_wallet(ctx, command, arg):
    if command != "check":
        await safe_send(ctx, "Slow down.\nFirst, check your wallet.\nType `!check wallet`")
        return True  # block command
    if command == "check" and arg[0]!= "wallet":
        await safe_send(ctx, "We are checking wallet only for now\n Use `check wallet`")
        return True

    gold = check_wallet(ctx.author.id)
    response = create_response("check_wallet", 1, user=ctx.author.mention, gold=gold, emoji=GOLD_EMOJI)
    await safe_send(ctx, response)

    await advance(ctx.author.id, TutorialState.PLAY)
    await asyncio.sleep(1.4)

    await safe_send(ctx, "Yes that's your balance not the highest but still something follow along and we are getting rich.\n\nThe `check` command works for other stats too — you’ll discover those later.\n\nNext step: let’s make money.\nType `!play`")

    return True

async def handle_play(ctx, command, arg):
    if command != "play":
        await safe_send(ctx, "Nuh uh! Good kids litsen to adults, now stop jumping around and do `!play`")
        return True
    await safe_send(ctx, "I’ll think of a number within a range.\nYou guess the number.\n\nGuess correctly → you advance and earn more rewards.\nGuess wrong → unlucky.\n\nLet’s begin.")
    # start the game (same logic as the command)
    await asyncio.sleep(3.5)
    guess = Guess()
    await guess.play_game(
        ctx,
        ctx.bot,
        sessions["guess"]       # same session registry used by the cog
    )

    await asyncio.sleep(2)
    await safe_send(ctx, "Nice.\n\nRemember the Bag of Gold I gave you?\nYou can use items with the `!use` command.\nExample: `!use bag of gold`\n\nNow let’s spend your gold.\nNext task: open the shop using `/shop`")
    await advance(ctx.author.id, TutorialState.OPEN_SHOP)
    return True


async def handle_open_shop(ctx, command, arg):
    if command not in ("use", "shop", "open"):
        await safe_send(ctx, "Before gambling your gold away, let’s visit the shop.\nUse `/shop`")
        return True

    if command == "shop":
        embed,view = daily_shop()
        await safe_send(ctx, embed=embed, view=view)
        await safe_send(ctx, "Buy anything you want. Intructions are at the bottom of shop embed\nYou can also sell items back using the Buyback button.\n\nOne final lesson left.\nNext task: earn gold by working.\nType `!work knight`")
        await advance(ctx.author.id, TutorialState.WORK)
        return True

    return False #let them run use and open commands

async def handle_work(ctx, command, arg):
    if command not in ("use", "work", "open", "buy"):
        await safe_send(ctx, "This is the final step.\nChoose a job to earn gold.\n\nExample: `!work knight`")
        return True

    if command == "work":
        valid_jobs = ("knight", "digger", "miner", "thief")
        job = arg[0].lower()
        if job not in valid_jobs:
            await safe_send(ctx, f"Available jobs: {', '.join(valid_jobs)}")
            return True

        worker = JobsClass(ctx.author.id)

        if job == "knight":
            result = worker.knight()
        elif job == "digger":
            result = worker.digger()
        elif job == "miner":
            result = worker.miner()
        elif job == "thief":
            result = "Nah come on lets not start with this as ur first job honesty is best policy try any of other three jobs"
            await safe_send(ctx, result)
            return True

        await safe_send(ctx, result)
        await advance(ctx.author.id, TutorialState.COMPLETED)
        await asyncio.sleep(1)
        await safe_send(ctx, "Working drains energy, you regain it over time check your current energy status with `!check energy`\nAnd with that you’re done.\n\nYou now know the basics.\nUse `/help` to see all commands.\nIf you’re confused about any command, ask me:\n`!commandhelp <command>`\n\nGood luck.\nAlso credited you with 50 chips ;) `!details gambling` if you don't wanna go in blind and loose it all")
        add_chip(ctx.author.id, 50)
        return True

    return False



STATE_HANDLERS = {
    TutorialState.NOT_STARTED: handle_not_started,
    TutorialState.CHECK_WALLET: handle_check_wallet,
    TutorialState.PLAY: handle_play,
    TutorialState.OPEN_SHOP: handle_open_shop,
    TutorialState.WORK: handle_work,
}

async def tutorial_guard(ctx, command_name, args):
    state = await get_tutorial_state(ctx.author.id)

    if state == TutorialState.COMPLETED:
        return False  # free user, do nothing

    handler = STATE_HANDLERS.get(state)
    if not handler:
        return False  # safety fallback

    block = await handler(ctx, command_name, args)
    return block

async def get_tutorial_state(user_id: int) -> TutorialState:
    with Session() as session:
        user = session.get(User, user_id)
        if not user:
            return TutorialState.NOT_STARTED

        try:
            return TutorialState(user.tutorial_state)
        except ValueError:
            return TutorialState.NOT_STARTED

async def advance(user_id: int, state: TutorialState):
    with Session() as session:
        user = session.get(User, user_id)
        if not user:
            return

        user.tutorial_state = int(state)
        session.commit()
