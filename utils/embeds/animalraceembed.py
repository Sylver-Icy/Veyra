"""
animalraceembed.py
------------------
Handles the creation of Discord embeds and UI views for the animal race system,
including race cooldowns, race start notifications, track visualization, and results.
"""

import discord

def race_cooldown_embed(cooldown_time: float):
    """
    Create an embed to notify users that a race just finished and a cooldown is active.

    Parameters:
        cooldown_time (float): Seconds remaining until the next race can be started.

    Returns:
        tuple: (discord.Embed, RemindMeButtonView) - The cooldown embed and a view with a "Remind Me" button.
    """
    embed = discord.Embed(
        title="🏁 A Race Just Finished!",
        description="A race took place in this server recently — wait till the next one :3\n\n"
                    "If you don’t wanna miss the next race, press the button below and I'll remind you!",
        color=discord.Color.gold()
    )
    # Footer includes cooldown info
    embed.set_footer(
        text=f"Next race can be started in {int(cooldown_time)} seconds \nConvert it into minutes yourself:3"
    )
    view = RemindMeButtonView()
    return embed, view


class RemindMeButtonView(discord.ui.View):
    """
    View containing a persistent 'Remind Me' button for users to opt-in for race reminders.
    Remembers users who requested reminders until the next race is started.
    """
    remind_set = set()

    @discord.ui.button(label="Remind Me", style=discord.ButtonStyle.primary, custom_id="remind_me")
    async def remind_me(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Handle the 'Remind Me' button click.
        Adds the user to the reminder set if not already present, and responds ephemerally.
        """
        user_id = interaction.user.id
        # Reminder handling: prevent duplicate reminders
        if user_id in self.remind_set:
            await interaction.response.send_message(
                "Chill dude, I already got you! I’ll remind you when the next race starts 😎",
                ephemeral=True
            )
        else:
            self.remind_set.add(user_id)
            await interaction.response.send_message(
                f"Got it! <@{user_id}> I’ll remind you when the next race begins 🏁",
                ephemeral=True
            )

def race_start_embed(starter: discord.User):
    """
    Create an embed announcing the start of a race and reminding users to place bets.

    Parameters:
        starter (discord.User): The user who started the race.

    Returns:
        tuple: (discord.Embed, str) - The race start embed and mention string for reminder users.
    """
    embed = discord.Embed(
        title="🏁 Race Incoming!",
        description=f"{starter.mention} wants to start a race!\n"
                    "The race will begin in **5 minutes** — place your bets now!",
        color=discord.Color.green()
    )
    # Mention users who requested reminders, if any
    mentions = " ".join(f"<@{uid}>" for uid in RemindMeButtonView.remind_set) if RemindMeButtonView.remind_set else ""
    embed.description += "\n\n🔔 Ding ding! Reminder for my forgetful crew — don't miss this race!"
    # Footer info for betting instructions
    embed.set_footer(
        text="Use `bet! <animal> <amount to bet>` to bet. \nAnimal name case insensitive btw:>"
    )
    return embed, mentions

def create_race_embed(positions: dict):
    """
    Create an embed visualizing the current state of the race track.

    Parameters:
        positions (dict): Mapping of animal emoji/name to their current position (int).

    Returns:
        discord.Embed: Embed showing the current race progress.
    """
    track_length = 30
    desc = ""
    # Track visualization: show each animal's progress on a line
    for animal, pos in positions.items():
        remaining = track_length - pos
        if remaining < 0:
            remaining = 0
        desc += f"🏁{'-' * remaining}{animal}\n"
    embed = discord.Embed(
        title="🐾 The Race is On!",
        description=desc,
        color=discord.Color.random()
    )
    return embed

def create_final_embed(positions: dict, winner: str):
    """
    Render the final race embed announcing the winner and showing final standings.

    Parameters:
        positions (dict): Mapping of animal emoji/name to steps traveled (int).
        winner (str): The animal emoji/name that won (e.g. '🐇').

    Returns:
        discord.Embed: Embed summarizing the race results.
    """
    track_length = 30
    # Build track lines with final positions, including numeric progress
    desc_lines = []
    for animal, pos in positions.items():
        remaining = track_length - pos
        if remaining < 0:
            remaining = 0
        desc_lines.append(f"🏁{'-' * remaining}{animal}  ({pos}/{track_length})")
    desc = "\n".join(desc_lines)
    title = f"🏁 {winner.capitalize()} wins the race! 🎉"
    embed = discord.Embed(
        title=title,
        description=desc,
        color=discord.Color.gold()
    )
    # Add a final standings field sorted by distance (desc)
    standings = sorted(positions.items(), key=lambda x: x[1], reverse=True)
    standings_text = "\n".join(f"{i+1}. {a} — {p} steps" for i, (a, p) in enumerate(standings))
    embed.add_field(name="Final Standings", value=standings_text, inline=False)
    # Footer includes reward info
    embed.set_footer(text="Distributing rewards... Good luck next time!")
    return embed
