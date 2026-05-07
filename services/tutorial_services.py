from enum import IntEnum

from discord import ApplicationContext


class TutorialState(IntEnum):
    NOT_STARTED = 0
    IN_TUTORIAL_BATTLE = 1
    COMPLETED = -1


ALLOWED_DURING_TUTORIAL = {
    "helloveyra",
    "help",
    "details",
    "profile",
}

TUTORIAL_BLOCK_MESSAGE = "Finish your starter duel with `!helloVeyra` first."


def _session_and_user_model():
    from database.sessionmaker import Session
    from models.users_model import User

    return Session, User


async def safe_send(ctx, content=None, **kwargs):
    if isinstance(ctx, ApplicationContext):
        if not ctx.response.is_done():
            await ctx.respond(content, **kwargs)
        else:
            await ctx.followup.send(content, **kwargs)
    else:
        await ctx.send(content, **kwargs)


def _normalize_command(value):
    if value is None:
        return ""
    return str(value).strip().lower()


async def tutorial_completed(user_id: int):
    Session, User = _session_and_user_model()
    with Session() as session:
        user = session.get(User, user_id)
        if not user:
            return False
        return _coerce_tutorial_state(user.tutorial_state) == TutorialState.COMPLETED


async def tutorial_guard(ctx, command_name, args):
    state = await get_tutorial_state(ctx.author.id)

    if state == TutorialState.COMPLETED:
        return False

    if _normalize_command(command_name) in ALLOWED_DURING_TUTORIAL:
        return False

    await safe_send(ctx, TUTORIAL_BLOCK_MESSAGE)
    return True


def _coerce_tutorial_state(raw_state) -> TutorialState:
    try:
        return TutorialState(raw_state)
    except ValueError:
        return TutorialState.NOT_STARTED


async def get_tutorial_state(user_id: int) -> TutorialState:
    Session, User = _session_and_user_model()
    with Session() as session:
        user = session.get(User, user_id)
        if not user:
            return TutorialState.NOT_STARTED

        return _coerce_tutorial_state(user.tutorial_state)


async def advance(user_id: int, state: TutorialState):
    Session, User = _session_and_user_model()
    with Session() as session:
        user = session.get(User, user_id)
        if not user:
            return

        user.tutorial_state = int(state)
        session.commit()
