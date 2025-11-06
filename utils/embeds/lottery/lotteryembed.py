import discord
from discord.ui import View, Button

from services.lottery_services import create_ticket, pick_lottery_winner, calculate_prize_pool
from services.economy_services import add_gold

from utils.emotes import GOLD_EMOJI


class LotteryButton(View):
    def __init__(self, ticket_price: int):
        super().__init__(timeout=None)
        self.ticket_price = int(ticket_price)
        self.children[0].label = f"🎟️ Buy Ticket {self.ticket_price} {GOLD_EMOJI}"

    @discord.ui.button(label="🎟️ Buy Ticket", style=discord.ButtonStyle.green)
    async def buy_ticket(self, button: Button, interaction: discord.Interaction):
        ticket_id = create_ticket(interaction.user.id, self.ticket_price)
        if ticket_id == 0:
            await interaction.response.send_message(
                "❌ Not enough gold! Maybe ask your friends to send you some?"
            )
        elif ticket_id == 1:
            await interaction.response.send_message(
                "Only my friends are allowed to enter this. Greet me first with `!helloVeyra`"
            )
        else:
            await interaction.response.send_message(
                f"✅ You bought a ticket, {interaction.user.name}! Your ticket number is `{ticket_id}`."
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
            description="No tickets were purchased this round.\nVeyra keeps the prize… again 😏",
            color=discord.Color.dark_grey()
        )
        return embed


    winner_id, ticket_id = result
    prize = calculate_prize_pool()
    embed = discord.Embed(
        title="🎉 Lottery Winner 🎊",
        description=f"The winning ticket number is **{ticket_id}**!\nOwned by <@{winner_id}>.",
        color=discord.Color.red()
    )

    embed.add_field(name=f"Congratulations on winning {prize} {GOLD_EMOJI}", value="Your winnings have been deposited")
    add_gold(winner_id, prize)

    return embed