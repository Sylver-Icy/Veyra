import discord
from datetime import datetime, timedelta, timezone

from domain.loans.rules import LOAN_OFFERS

from utils.emotes import GOLD_EMOJI


def build_loan_terms_embed(loan_id: str = "0") -> discord.Embed:
    """Build a clean loan terms embed for the given loan offer id."""
    loan_id = str(loan_id).strip()
    offer = LOAN_OFFERS.get(loan_id)

    if not offer:
        return discord.Embed(
            title="❌ Unknown Loan Offer",
            description=f"No loan offer found for id **{loan_id}**.",
        )

    principal = offer.get("principal", 0)
    interest_rate = offer.get("interest_rate", 0)
    term_days = offer.get("term_days", 0)

    # Repayment amount:
    # - If repay_amount is set (>0), use it
    # - Else treat it as an interest-based plan
    repay_amount = offer.get("repay_amount", 0) or 0
    if repay_amount <= 0:
        repay_amount = int(round(principal * (1 + (interest_rate * term_days))))

    due_date = datetime.now(timezone.utc) + timedelta(days=term_days)
    due_date_str = f"<t:{int(due_date.timestamp())}:R>"  # Discord relative timestamp

    embed = discord.Embed(
        title=f"📜 {offer.get('name', 'Loan Terms')}",
        description=(
            f"{offer.get('desc', 'You are about to take a loan.')}\n\n"
            f"You are about to take this loan. Review the terms carefully:"
        ),
    )

    embed.add_field(name="You Receive", value=f"**{principal}** {GOLD_EMOJI}", inline=True)
    embed.add_field(name="Interest", value=f"**{interest_rate * 100:.2f}% / day**" if interest_rate else "**0%**", inline=True)
    embed.add_field(name="Repay", value=f"**{repay_amount}** {GOLD_EMOJI}", inline=True)

    embed.add_field(name="Due", value=due_date_str, inline=False)

    embed.add_field(
        name="⚠️ Default Warning",
        value=(
            "If you fail to repay on time:\n"
            "• Your **credit score will drop**\n"
            "• You may be **blocked from taking new loans**"
        ),
        inline=False,
    )

    return embed
