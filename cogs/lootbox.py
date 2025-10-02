import logging
from discord.ext import commands
from services.inventory_services import give_item, take_item
from services.lootbox_services import lootbox_reward, user_lootbox_count
from services.economy_services import add_gold
from utils.itemname_to_id import item_name_to_id

logger = logging.getLogger(__name__)

class Lootbox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def open(self, ctx, *, lootbox_name: str):
        """Open a lootbox and receive a random reward."""
        lootbox_amount = user_lootbox_count(ctx.author.id, lootbox_name)

        # Invalid lootbox
        if lootbox_amount == -1:
            await ctx.send(
                "❌ Incorrect box name. Available boxes are:\n"
                "• Wooden Box\n"
                "• Stone Box\n"
                "• Iron Box\n"
                "• Platinum Box\n"
                "Choose wisely :)"
            )
            return

        # No lootboxes of this type
        if lootbox_amount == 0:
            await ctx.send(f"You don’t have any **{lootbox_name.title()}**. What are you tryna open, huh?")
            return

        # Consume one lootbox
        item_id = item_name_to_id.get(lootbox_name.lower())
        if not item_id:
            await ctx.send(f"❌ `{lootbox_name}` doesn’t exist in my database. Skill issue?")
            return

        take_item(ctx.author.id, item_id, 1)

        # Get reward
        reward = lootbox_reward(lootbox_name)

        if "Gold" in reward:
            gold_amount = reward["Gold"]
            await ctx.send(f"💰 You got **{gold_amount} Gold**!!!")
            add_gold(ctx.author.id, gold_amount)
            logger.info("Gold recieved from %s", lootbox_name, extra={
                "user": ctx.author.name,
                "flex": f"Gold received, {gold_amount}",
                "cmd": "open"
            })
        else:
            rarity = reward.get("Rarity", "Unknown")
            item = reward.get("Item", "???")
            await ctx.send(
                f"🎉 You got a **{rarity}** item!\n"
                f"✨ It isssss... **{item}**. Let’s Goooooo!"
            )

            reward_id = item_name_to_id.get(item.lower())
            if reward_id:
                give_item(ctx.author.id, reward_id, 1)
                logger.info("Items received from %s box", lootbox_name, extra={
                    "user": ctx.author.name,
                    "flex": f"items received {item}",
                    "cmd": "open"
                })
            else:
                await ctx.send(f"⚠️ Couldn’t add `{item}` to your inventory (not found in database).")


def setup(bot):
    bot.add_cog(Lootbox(bot))