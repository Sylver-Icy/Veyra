import random
import discord
from discord.ui import View, button, Button

from services.profession.contractor.moonroot_services import prune_tree
from services.profession.contractor.sylphs_services import spawn_sylph

PRUNE_DIALOGUES = [
    "You snip a tiny glowing leaf. The Moonroot shivers politely. ✂️",
    "Soft whispers echo as your scissors glide through silver vines.",
    "The Moonroot wiggles like it’s ticklish. This is mildly unsettling.",
    "A sleepy sylph peeks out, judges your technique, then vanishes.",
    "You trim a stubborn branch. It refuses, then gives in dramatically.",
    "A butterfly made of moonlight flutters past your face.",
    "The tree hums like it’s enjoying spa day.",
    "A shower of pale petals drifts downward.",
    "You swear the Moonroot sighed contentedly.",
    "A branch curls away from your scissors like ‘nope’.",
    "You carefully trim a crescent-shaped leaf.",
    "A faint pulse of light travels up the trunk.",
    "The Moonroot rustles despite the lack of wind.",
    "Tiny sparks drift where your scissors passed.",
    "A hidden sylph giggles somewhere above you.",
    "The bark feels warm, almost alive.",
    "You remove a tangled silver vine.",
    "The canopy glows a little brighter.",
    "A petal lands on your shoulder and dissolves.",
    "The Moonroot seems pleased with your work.",
    "You tease apart two vines locked in an eternal leafy argument.",
    "A shimmer runs along the bark like a sleepy stretch.",
    "Your scissors catch the light, briefly blinding absolutely no one.",
    "A tiny mote of glow floats up, then pops like a silent bubble.",
    "The Moonroot tilts ever so slightly toward you.",
    "You trim with surgical precision. The tree remains unimpressed.",
    "A silver leaf spirals down in slow, theatrical defeat.",
    "Somewhere, a sylph offers sarcastic applause.",
    "You snip. The canopy answers with a gentle ripple.",
    "A pale glow gathers at the cut, then fades.",
    "The branch recoils, then pretends it meant to.",
    "A dusting of luminous pollen hangs in the air.",
    "The Moonroot hum deepens, low and velvety.",
    "You free a knot of vines. They look offended.",
    "A ghostly petal passes straight through your hand.",
    "You swear the roots shifted underfoot.",
    "A quiet sparkle lingers where the blade moved.",
    "The tree rustles like it’s whispering secrets.",
    "A crescent leaf falls and melts into light.",
    "You prune a twig that absolutely had it coming.",
    "A flicker darts between the branches and vanishes.",
    "The Moonroot glows with mild approval.",
    "Your careful cut earns a soft pulse of silver.",
    "A vine slides away like it’s dodging responsibility.",
    "Tiny lights scatter like startled fireflies.",
    "You trim a stubborn shoot into submission.",
    "The canopy sighs in leafy resignation.",
    "A soft chime echoes from nowhere obvious.",
    "You tidy a cluster of overgrown leaves.",
    "A faint glow trails behind your scissors.",
    "The Moonroot shivers, then settles.",
    "A petal bursts into glitter midair.",
    "You snip with confidence bordering on arrogance.",
    "A sylph’s laughter rings out, distant and brief.",
    "The bark warms beneath your touch.",
    "A lazy sparkle drifts toward the sky.",
    "You clip a vine that clearly ignored boundaries.",
    "The tree answers with a pleased rustle.",
    "A glow blooms, then dims like a heartbeat.",
    "You step back. The Moonroot looks refreshed."
]


def create_prune_embed(tree_id: int, user_id: int):
    embed = discord.Embed(
        title="🌙 Moonroot Care",
        description="You approach the Moonroot with pruning shears...",
        color=discord.Color.dark_teal()
    )

    embed.set_footer(text="Press the button to begin pruning ✂️")

    view = PruneView(tree_id=tree_id, user_id=user_id)
    return embed, view

# --- Sylph naming modal and view ---
class SylphNameModal(discord.ui.Modal):
    def __init__(self, user_id: int, tree_id: int):
        super().__init__(title="Name Your Sylph")
        self.user_id = user_id
        self.tree_id = tree_id

        self.name_input = discord.ui.InputText(
            label="Sylph Name",
            placeholder="Enter a mystical (or ridiculous) name...",
            max_length=32
        )

        self.add_item(self.name_input)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            name = self.name_input.value

            sylph_id = spawn_sylph(
                user_id=self.user_id,
                tree_id=self.tree_id,
                name=name
            )

            embed = discord.Embed(
                title="✨ Sylph Named",
                description=f"Your baby sylph is now called **{name}**",
                color=discord.Color.blurple()
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"Sylph naming failed: {e}",
                ephemeral=True
            )


class SylphNamingView(View):
    def __init__(self, user_id: int, tree_id: int):
        super().__init__(timeout=160)
        self.user_id = user_id
        self.tree_id = tree_id

    @button(label="Name ✨", style=discord.ButtonStyle.primary)
    async def name_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Not your sylph. Hands off.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(SylphNameModal(self.user_id, self.tree_id))

    @button(label="Skip", style=discord.ButtonStyle.secondary)
    async def skip_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Not your decision to make.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🌿 Sylph Unnamed",
            description="The baby sylph drifts away, nameless but free.",
            color=discord.Color.dark_teal()
        )

        self.disable_all_items()
        await interaction.response.edit_message(embed=embed, view=self)


def create_sylph_spawn_embed(user_id: int, tree_id: int):
    embed = discord.Embed(
        title="✨ A New Sylph",
        description="A baby sylph emerges from the Moonroot’s glowing roots.\nDo you want to give it a name?",
        color=discord.Color.dark_teal()
    )

    embed.set_footer(text="Choose wisely. Names are forever (probably).")

    view = SylphNamingView(user_id=user_id, tree_id=tree_id)
    return embed, view

class PruneView(View):
    def __init__(self, tree_id: int, user_id: int):
        super().__init__(timeout=160)
        self.tree_id = tree_id
        self.user_id = user_id
        self.clicks = 0
        self.max_clicks = random.randint(1, 2)
        self.last_dialogue = None

    @button(label="Prune ✂️", style=discord.ButtonStyle.secondary)
    async def prune_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This is not your Moonroot to butcher ",
                ephemeral=True
            )
            return

        self.clicks += 1

        if self.clicks < self.max_clicks:
            dialogue = random.choice(PRUNE_DIALOGUES)

            while dialogue == self.last_dialogue:
                dialogue = random.choice(PRUNE_DIALOGUES)

            self.last_dialogue = dialogue

            embed = discord.Embed(
                title="🌙 Pruning the Moonroot",
                description=dialogue,
                color=discord.Color.dark_teal()
            )

            await interaction.response.edit_message(embed=embed, view=self)
            return

        msg, spawn_possible = prune_tree(self.tree_id)

        embed = discord.Embed(
            title="✨ Pruning Complete",
            description=msg,
            color=discord.Color.green()
        )

        self.disable_all_items()
        await interaction.response.edit_message(embed=embed, view=self)

        if spawn_possible:
            spawn_embed, spawn_view = create_sylph_spawn_embed(
                user_id=self.user_id,
                tree_id=self.tree_id
            )
            await interaction.followup.send(
                content=f"{interaction.user.mention}",
                embed=spawn_embed,
                view=spawn_view
            )