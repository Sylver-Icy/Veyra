import discord



class DisableNotificationsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Disable Notifications",
        style=discord.ButtonStyle.danger,
        custom_id="disable_notifications"
    )
    async def disable_btn(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        from services.notif_services import disable_notif

        disable_notif(interaction.user.id)

        await interaction.response.send_message(
            "🔕 Notifications disabled.",
            ephemeral=True
        )


def build_notification_embed(data: dict):
    """
    data = {
        "heading": "⚡ Energy Full",
        "content": "Your energy has fully regenerated. Time to grind.",
        "footer": "Veyra Notifications",          # optional
        "color": 0x2ECC71                         # optional
    }
    Returns: (discord.Embed, discord.ui.View)
    """

    heading = data.get("heading", "Notification")
    content = data.get("content", "")
    footer = data.get("footer", "")
    color = data.get("color", 0x5865F2)  # Discord blurple default

    embed = discord.Embed(
        title=heading,
        description=content,
        color=color
    )

    if footer:
        embed.set_footer(text=footer)

    view = DisableNotificationsView()

    return embed, view