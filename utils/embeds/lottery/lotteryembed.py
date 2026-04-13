import discord
from discord.ui import View, Button

from services.game_events_services import create_game_event
from services.lottery_services import (
    calculate_prize_pool,
    create_ticket,
    get_lottery_round_entries,
    get_lottery_stats,
    pick_lottery_winner,
)
from services.economy_services import add_gold
from services.users_services import update_biggest_lottery_win
from utils.custom_errors import UserNotRegisteredError

from utils.emotes import GOLD_EMOJI


class LotteryButton(View):
    def __init__(self, ticket_price: int):
        super().__init__(timeout=None)
        self.ticket_price = int(ticket_price)
        self.children[0].label = f"🎟️ Buy Ticket {self.ticket_price}"

    @discord.ui.button(label="🎟️ Buy Ticket", style=discord.ButtonStyle.green)
    async def buy_ticket(self, _button: Button, interaction: discord.Interaction):
        try:
            ticket_id = create_ticket(interaction.user.id, self.ticket_price)
        except UserNotRegisteredError:
            await interaction.response.send_message(
                f"{interaction.user.mention} you need to use `!helloVeyra` first to participate in the lottery."
            )
            return

        if ticket_id == 0:
            await interaction.response.send_message(
                f"❌ {interaction.user.mention} you don’t have enough gold to buy a lottery ticket. Maybe ask your friends to send some?"
            )
        else:
            tickets_sold , prize_pool = get_lottery_stats()
            await interaction.response.send_message(
                f"✅ You bought a ticket, <@{interaction.user.id}>! Your ticket number is `{ticket_id}`.\n 🎫 Tickets Sold: {tickets_sold}\nTotal Prize Pool: {prize_pool}{GOLD_EMOJI}"
            )


def create_lottery_embed(ticket_price):
    embed = discord.Embed(
        title="🎰 Veyra’s Lottery",
        description="Feeling lucky? Wanna try your luck?\nPress the button below to buy a ticket!",
        color=discord.Color.gold(),
    )
    view = LotteryButton(ticket_price)
    return embed, view


def create_result_embed():
    result = pick_lottery_winner()
    if not result:
        embed = discord.Embed(
            title="🎟️ Lottery Results",
            description="No tickets were purchased this round.",
            color=discord.Color.dark_grey()
        )
        return embed, None


    participants = get_lottery_round_entries()
    winner_id, ticket_id = result
    prize = calculate_prize_pool()
    embed = discord.Embed(
        title="🎉 Lottery Winner 🎊",
        description=f"The winning ticket number is **{ticket_id}**!\nOwned by <@{winner_id}>.",
        color=discord.Color.red()
    )

    embed.add_field(name=f"Congratulations on winning {prize} {GOLD_EMOJI}", value="Your winnings have been deposited")
    add_gold(winner_id, prize)
    update_biggest_lottery_win(winner_id, prize)

    winner_ticket_count = next(
        (entry["ticket_count"] for entry in participants if entry["user_id"] == winner_id),
        1,
    )
    create_game_event(
        winner_id,
        "lottery_win",
        f"Won the lottery with {winner_ticket_count} ticket(s) and pocketed {prize} gold.",
        {
            "ticket_id": ticket_id,
            "ticket_count": winner_ticket_count,
            "prize": prize,
        },
    )

    for entry in participants:
        if entry["user_id"] == winner_id:
            continue
        create_game_event(
            entry["user_id"],
            "lottery_loss",
            f"Bought {entry['ticket_count']} lottery ticket(s) and still lost the draw.",
            {
                "ticket_count": entry["ticket_count"],
                "prize_pool": prize,
                "winning_ticket": ticket_id,
            },
        )

    return embed, winner_id
