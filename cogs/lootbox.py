from discord.ext import commands
from services.inventory_services import give_item
from services.lootbox_services import lootbox_reward, user_lootbox_count
from services.economy_services import add_gold
from utils.itemname_to_id import item_name_to_id

class Lootbox(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    async def open(self,ctx,*,lootbox_name):
        lootbox_amount = user_lootbox_count(ctx.author.id, lootbox_name)
        if lootbox_amount == -1:
            await ctx.send(
                """Incorrect box name. There are only 4 types of boxes:
    • Wooden Box
    • Stone Box
    • Iron Box
    • Platinum Box
Choose among these :)"""
            )
        elif lootbox_amount == 0:
            await ctx.send(f"You don't have any {lootbox_name.title()}. What are you tryna open? Huh")
        else:
            item_id = item_name_to_id[lootbox_name.lower()]
            give_item(ctx.author.id, item_id, -1) #Passing negative value to deduct 1 box from user inventory
            reward = lootbox_reward(lootbox_name)
            if "Gold" in reward:
                await ctx.send(f"You got {reward['Gold']} Gold!!!")
                add_gold(ctx.author.id, reward["Gold"])
            else:
                await ctx.send(f"You got a {reward['Rarity']} item :O and it isssss... a {reward['Item']}. Let's Gooooooooo")
                reward_id = item_name_to_id[(reward["Item"]).lower()]
                give_item(ctx.author.id,reward_id,1)

def setup(bot):
    bot.add_cog(Lootbox(bot))