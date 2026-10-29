import discord
from discord.ext import commands
from discord import app_commands
from utils import ids

GUILD_ID = ids.my_guild_id
MOD_ROLE = ids.mod_role_id

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create-ticket", description="Create a private ticket channel for support.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def create_ticket(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            guild = interaction.guild

            # Find or create category
            category = discord.utils.get(guild.categories, name="TICKETS")
            if not category:
                category = await guild.create_category("TICKETS")

            # Create channel
            ticket_channel = await category.create_text_channel(f'ticket-{interaction.user.name}')

            # Set permissions
            await ticket_channel.set_permissions(guild.default_role, view_channel=False)
            await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

            # Mention mod role
            mod_role = guild.get_role(MOD_ROLE) 
            if mod_role:
                await ticket_channel.set_permissions(mod_role, view_channel=True, send_messages=True)

            # Send message in the ticket
            embed = discord.Embed(
                title="Ticket Created",
                description="A staff member will be with you shortly.",
            )
            embed.set_thumbnail(url=guild.icon.url)
            embed.add_field(name="Created By", value=interaction.user.mention)

            await ticket_channel.send(content=f"{mod_role.mention}{interaction.user.mention}" if mod_role else f"{interaction.user.mention}", embed=embed)
            await interaction.followup.send(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)
        except Exception as e:
            print(e)


async def setup(bot: commands.Bot):
    await bot.add_cog(Ticket(bot))