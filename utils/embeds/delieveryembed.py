import discord
from utils.emotes import GOLD_EMOJI
from services.economy_services import add_gold
from services.exp_services import add_exp
# 1. Define a custom View that stores the original user's ID
class DeliveryView(discord.ui.View):
    def __init__(self, user_id: int, items: dict, reward: int, reroll_cost: int):
        super().__init__(timeout=100)
        self.user_id = user_id
        self.items = items
        self.reward = reward
        self.reroll_cost = reroll_cost
        self.reroll_quest.label = f"Reroll ({self.reroll_cost}G)"

    @discord.ui.button(label="Deliver Items", style=discord.ButtonStyle.green, custom_id="deliver_items_button", emoji="📦")
    async def deliver_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Button to deliver the items
        takes reuired items from user if available and grants them reward
        deletes the active quest and create a new one
        """

        #Check if the user clicking is the same as the one allowed
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This button isn't for you!", ephemeral=True)
            return

        from services.delievry_minigame_services import items_check,delete_quest,create_quest #lazy import to avoid circular import

        if items_check(self.user_id,self.items): #checks if user has enough items and if delivery succeed
            add_gold(self.user_id, self.reward) #gives the gold for quest
            delete_quest(self.user_id, True, False) #delete the current
            create_quest(self.user_id,True) #create a new quest
            add_exp(self.user_id, 50)
            await interaction.response.edit_message(content="✅ You delivered the items!", embed=None, view=None)

        else:
            button.disabled =True
            await interaction.response.edit_message(
                content="You don't have all the required items right now use `/quest` again once u r done gathering em",
                view=self
                )

    @discord.ui.button(label="Skip Request", style=discord.ButtonStyle.blurple, custom_id="skip_request_button", emoji="🚫")
    async def skip_button(self,button: discord.ui.Button, interaction: discord.Interaction):
        """
        Skips the active quest and gives a new one
        """
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This button isn't for you!", ephemeral=True)
            return
        from services.delievry_minigame_services import delete_quest, create_quest
        if delete_quest(self.user_id):
            create_quest(self.user_id)
            #disable the button after use well i'm deleting entire embed so this is lowkey useless
            button.disabled = True
            await interaction.response.edit_message(content="Request skipped use /quest again to get new request", embed=None, view=None)
            return
        else:
            button.disabled = True
            await interaction.response.edit_message(content="You have already used your 3 skips Today", view=self)
            return

    @discord.ui.button(label="Reroll", style=discord.ButtonStyle.gray, custom_id="reroll_button", emoji="🎲")
    async def reroll_quest(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Rerolls the quest without breaking streak."""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This button isn't for you!", ephemeral=True)
            return
        from services.delievry_minigame_services import reroll_quest
        response = reroll_quest(self.user_id)
        button.disabled = True
        await interaction.response.edit_message(content=response, embed=None, view=None)
        return




def delievery_embed(user_name: str, items: dict, reward: int, user_id: int, streak: int, reroll_cost: int):
    embed = discord.Embed(
        title=f"Hii! {user_name},        🔥STREAK  **{streak}**",
        description="People in town need some items, do you have them? You will be rewarded!",
        color=discord.Colour.dark_blue()
    )

    for item_name, amount in items.items():
        embed.add_field(
            name=f"{amount}X {item_name}",
            value=" ",
            inline=False
        )

    embed.add_field(
        name="Your reward: ",
        value=f"{reward}X {GOLD_EMOJI}",
        inline=False
    )

    return embed, DeliveryView(user_id, items, reward, reroll_cost)
