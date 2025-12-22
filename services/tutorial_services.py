import asyncio

from discord import ApplicationContext

from enum import IntEnum

from database.sessionmaker import Session
from models.users_model import User

from services.inventory_services import give_item
from services.guessthenumber_services import Guess
from services.shop_services import daily_shop
from services.jobs_services import JobsClass

from utils.global_sessions_registry import sessions


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
    await safe_send(ctx, "Let's teach you how to survive in Natlade dw I'll take it slow\n first do `check wallet` we gonna check how much stonks you got :D")
    await advance(ctx.author.id, TutorialState.CHECK_WALLET)
    return True

async def handle_check_wallet(ctx, command, arg):
    if command != "check":
        await safe_send(ctx, "How are you gonna get rich if you don't realise you are poor?? hmm? come on just type `!check wallet`")
        return True  # block command

    await advance(ctx.author.id, TutorialState.PLAY)
    await asyncio.sleep(1)
    await safe_send(ctx, "HAHA! Brokie!!!\nAww dw here take these bags of gold :3\nRn you checked your wallet the `check` command can accept other arguments as well to check your other stats\nAlr time to make more cash now do `!play`")
    if not await tutorial_completed(ctx.author.id):
        give_item(ctx.author.id, 183, 2)

    return False

async def handle_play(ctx, command, arg):
    if command != "play":
        await safe_send(ctx, "Nuh uh! Good kids litsen to adults, now stop jumping around and do `!play`")
        return True
    await safe_send(ctx, "okay so i'll give you a number range and you will have to pick a number if you guess correctly we move to next stage else gg... and ofc bigger the stage bigger is reward")
    # start the game (same logic as the command)
    guess = Guess()
    await guess.play_game(
        ctx,
        ctx.bot,
        sessions["guess"]       # same session registry used by the cog
    )

    await asyncio.sleep(1)
    await safe_send(ctx, "ehe stacking rewards;) remeber the bag of gold I gave you? use it with `use` <- this lets you use any usable item item\n just do `!use bag of gold`\ntime to go shopping!! you next task -> `/shop` its a slash command so dont type in chat like monkey")
    await advance(ctx.author.id, TutorialState.OPEN_SHOP)
    return True


async def handle_open_shop(ctx, command, arg):
    if command not in ("use", "shop", "open"):
        await safe_send(ctx, "Calm down lil wind!! Let's spend the gold you have before you loose it in gambling ->`/shop`<- :D")
        return True

    if command == "shop":
        embed,view = daily_shop()
        await safe_send(ctx, embed=embed, view=view)
        await safe_send(ctx, "Just buy whatever you want, There is also a buyback button you can sell stuff back to me as well\n You are so close to be a rich tycoon of Natlade, Next I'll show you one last way to make GOLD type `!work knight`")
        await advance(ctx.author.id, TutorialState.WORK)
        return True

    return False #let them run use and open commands

async def handle_work(ctx, command, arg):
    if command not in ("use", "work", "open"):
        await safe_send(ctx, "This is last step then you explore entire thing on your own and free to get lost :) DO `!work knight` ALREADY")
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
        await safe_send(ctx, "You are on your own now :D \n Use `/help` to list all the commands and if you get confused with any command lets say `buy`\n just ask me to explain it by `!commandhelp buy`\nGOOD LUCK!! Be the richest in server!!!")
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
