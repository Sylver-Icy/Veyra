from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional

from sqlalchemy import select, update

from database.sessionmaker import Session

from services.economy_services import remove_gold

from models.users_model import Loan, User

from domain.loans.rules import get_loan_details

from utils.custom_errors import NotEnoughGoldError
from utils.emotes import GOLD_EMOJI

ACTIVE_LOAN_STATUS = "active"
REMINDER_WINDOW_DAYS = 2


def issue_loan(user_id: int, loan_pack_id: str) -> Tuple[bool, Optional[int], Optional[Loan]]:
    """Issue a loan to a user if they don't already have an active one. Does not check ANYTHING ELSE

    Returns:
        (ok, active_pack_id, loan_row)

        - ok=True: loan was created, loan_row is returned
        - ok=False: user already has an active loan, active_pack_id contains the existing pack id

    Notes:
        - This function only creates the `loans` record.
        - It does NOT credit gold
    """
    loan = get_loan_details(loan_pack_id)
    duration_days = loan["term_days"]

    with Session() as session:
        # Check if user already has an active loan
        existing_active: Loan | None = session.execute(
            select(Loan)
            .where(Loan.user_id == user_id)
            .where(Loan.status == ACTIVE_LOAN_STATUS)
            .limit(1)
        ).scalar_one_or_none()

        if existing_active is not None:
            # already has an active loan
            return False, int(existing_active.loan_pack_id), None

        # Create new loan record
        now = datetime.now(timezone.utc)
        due_date = now + timedelta(days=duration_days)

        new_loan = Loan(
            user_id=user_id,
            loan_pack_id=int(loan_pack_id),
            status=ACTIVE_LOAN_STATUS,
            issued_at=now,
            due_date=due_date,
        )

        # Mark starter loan as given
        session.execute(
            update(User)
            .where(User.user_id == user_id)
            .where(User.starter_loan_given.is_(False))
            .values(starter_loan_given=True)
        )

        session.add(new_loan)
        session.commit()
        session.refresh(new_loan)

        return True, None, new_loan


def repay_loan(user_id: int) -> str:
    """Fetch the user's active loan row and repay it.

    Returns:
        (ok, message, loan_row)

        - ok=True: repayment succeeded
        - ok=False: repayment failed, message explains why

    Notes:
        - Currently assumes starter loan repayment amount is 2000.
        - TODO: support multiple loan types dynamically.
    """
    with Session() as session:
        active_loan: Loan | None = session.execute(
            select(Loan)
            .where(Loan.user_id == user_id)
            .where(Loan.status == ACTIVE_LOAN_STATUS)
            .limit(1)
        ).scalar_one_or_none()

        if active_loan is None:
            return "You have no loan you can take with `/loan`"

        try:
            remove_gold(user_id, 2000, session)
        except NotEnoughGoldError:
            return f"You need 2000 {GOLD_EMOJI} to repay your current debt"

        now = datetime.now(timezone.utc)

        # mark as paid
        session.execute(
            update(Loan)
            .where(Loan.id == active_loan.id)
            .values(status="paid", paid_at=now)
        )
        session.commit()

        # Detach-safe return
        session.commit()
        return "✅ Repaid your loan."


def check_starter_loan_given(user_id: int) -> bool:
    # Check if the user has already been given a starter loan
    with Session() as session:
        starter_given = session.execute(
            select(User.starter_loan_given)
            .where(User.user_id == user_id)
            .limit(1)
        ).scalar_one_or_none()

        return bool(starter_given)


async def send_due_loan_reminders(bot) -> int:
    """Send a DM reminder to users who have an active loan due within 2 days.

    Returns:
        int: number of DMs successfully sent
    """
    import discord

    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=REMINDER_WINDOW_DAYS)

    sent = 0

    with Session() as session:
        # Query all active loans due within the reminder window
        due_loans = session.execute(
            select(Loan)
            .where(Loan.status == ACTIVE_LOAN_STATUS)
            .where(Loan.due_date <= cutoff)
            .where(Loan.due_date > now)
        ).scalars().all()

    # Send DMs outside the DB session
    for loan in due_loans:
        try:
            user = bot.get_user(int(loan.user_id))
            if user is None:
                user = await bot.fetch_user(int(loan.user_id))

            if user is None:
                continue

            due_unix = int(loan.due_date.timestamp())
            loan_details = get_loan_details(str(loan.loan_pack_id))
            print(loan_details)

            loan_name = loan_details["name"]
            principal = loan_details["principal"]

            embed = discord.Embed(
                title="📬 Debt Collection Notice",
                description=(
                    "Your loan repayment is coming up.\n\n"
                    f"🧾 **Loan Pack:** `{loan_name}`\n"
                    f"🕒 **Time left:** <t:{due_unix}:R>\n\n"
                    "If you default, your credit score gets cooked and Veyra never will lend "
                    "you again 😇\n Pay now with `!repayloan`"
                ),
                color=discord.Color.gold(),
                timestamp=now,
            )

            embed.add_field(name="Amount", value=f"{principal}G", inline=True)
            embed.add_field(name="Due", value=f"<t:{due_unix}:f>", inline=True)
            embed.add_field(name="Time left", value=f"<t:{due_unix}:R>", inline=True)

            embed.set_footer(text="Veyra Finance Dept. | Pay up before we get creative")

            await user.send(embed=embed)
            sent += 1

        except discord.Forbidden:
            # User has DMs closed
            continue
        except Exception as e:
            print("send_due_loan_reminders error:", e)

    return sent