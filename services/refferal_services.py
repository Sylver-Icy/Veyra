"""
Referral / Invite Tracking Service

Responsible for:
- Storing inviter -> invited relationships
- Tracking successful invites (level 5 reached)
- Providing invite statistics
- Detecting which Discord invite was used on join

Design Goals:
- No reward is granted on join
- Rewards are granted only when invited user reaches level 5
- Only Veyra's main server is tracked
"""

from sqlalchemy import select, func

from database.sessionmaker import Session
from models.users_model import Invites
from services.users_services import is_user


# ============================================================
# DATABASE OPERATIONS
# ============================================================

def add_new_invite(inviter_id: int, invited_id: int):
    """
    Stores a new inviter -> invited relationship.

    Called when a member joins and we successfully detect
    which invite link was used.

    This does NOT grant rewards.
    """

    with Session() as session:

        # Inviter must be a registered Veyra user
        if not is_user(inviter_id, session):
            return

        # Prevent duplicate invited users
        exists = session.execute(
            select(Invites).where(Invites.invited_id == invited_id)
        ).scalar_one_or_none()

        if exists:
            return

        entry = Invites(
            inviter_id=inviter_id,
            invited_id=invited_id,
        )

        session.add(entry)
        session.commit()


def mark_inv_successful(inviter_id: int, invited_id: int):
    """
    Marks an invite as successful.

    Called when invited user reaches level 5.
    """

    with Session() as session:
        row = session.get(Invites, (inviter_id, invited_id))

        if not row:
            return

        row.rewarded = True
        
        session.commit()


def get_inviter(invited_id: int):
    """
    Returns inviter_id for a given invited user
    if they were invited and not yet rewarded.
    """

    with Session() as session:
        stmt = select(Invites.inviter_id).where(
            Invites.invited_id == invited_id,
            Invites.rewarded == False
        )

        return session.execute(stmt).scalar_one_or_none()


def count_total_invites(user_id: int):
    """
    Returns total number of people user has invited.
    """

    with Session() as session:
        stmt = select(func.count()).where(
            Invites.inviter_id == user_id
        )

        return session.execute(stmt).scalar_one()


def count_total_successful_invites(user_id: int):
    """
    Returns number of successful invites
    (invited users who reached level 5).
    """

    with Session() as session:
        stmt = select(func.count()).where(
            Invites.inviter_id == user_id,
            Invites.rewarded == True
        )

        return session.execute(stmt).scalar_one()


# ============================================================
# DISCORD INVITE TRACKING
# ============================================================

# Stores invite snapshots for Veyra's main guild
INVITE_CACHE = {}


async def create_inv_cache(bot, main_guild_id: int = 1275870089228320768):
    """
    Creates initial snapshot of invite usage.

    Call once inside on_ready().
    """

    guild = bot.get_guild(main_guild_id)
    if not guild:
        return

    invites = await guild.invites()
    INVITE_CACHE[main_guild_id] = invites


async def handle_member_join(bot, member, main_guild_id: int = 1275870089228320768):
    """
    Detects which invite link was used when a member joins
    and stores inviter -> invited relationship.

    Call inside on_member_join().
    """

    guild = bot.get_guild(main_guild_id)
    if not guild:
        return

    # Invites before join
    before = INVITE_CACHE.get(main_guild_id, [])

    # Invites after join
    after = await guild.invites()

    # Update cache immediately
    INVITE_CACHE[main_guild_id] = after

    used_invite = None

    # Compare invite usage counts
    for new in after:
        for old in before:
            if new.code == old.code and new.uses > old.uses:
                used_invite = new
                break
        if used_invite:
            break

    if not used_invite:
        return

    inviter_id = used_invite.inviter.id
    invited_id = member.id

    add_new_invite(inviter_id, invited_id)
