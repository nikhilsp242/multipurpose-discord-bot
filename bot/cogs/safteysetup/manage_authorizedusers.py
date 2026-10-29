import discord
from discord.ext import commands
from discord import app_commands
import typing
from models.authorizedusers import AuthorizedUsers

class ManageAuth(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="authorized-users", description="Manage authorized users")
    @app_commands.guilds(discord.Object(id=1183064183646982164))
    @app_commands.describe(action="What do you want to do", user="The user to add or remove")
    async def manage_auth(self, interaction: discord.Interaction, action: typing.Literal["Add", "Remove", "Show"], user: typing.Optional[discord.Member] = None):
        if interaction.user.id != interaction.guild.owner_id:
            return await interaction.response.send_message(
                "❌ Only the server owner can use this command.",
                ephemeral=True
            )
        user_id = str(user.id) if user else None
        guild_id = str(interaction.guild.id)

        if action == "Add":
            if not user:
                return await interaction.response.send_message("⚠️ Please specify a user to add.", ephemeral=True)
            if AuthorizedUsers.get_one(user_id, guild_id):
                return await interaction.response.send_message(f"🔁 {user.mention} is already an authorized user.", ephemeral=True)
            AuthorizedUsers.save(user_id, guild_id)
            await interaction.response.send_message(f"✅ {user.mention} has been added as an authorized user.", ephemeral=True)

        elif action == "Remove":
            if not user:
                return await interaction.response.send_message("⚠️ Please specify a user to remove.", ephemeral=True)
            if not AuthorizedUsers.get_one(user_id, guild_id):
                return await interaction.response.send_message(f"🚫 {user.mention} is not in the authorized users list.", ephemeral=True)
            AuthorizedUsers.remove(user_id, guild_id)
            await interaction.response.send_message(f"✅ {user.mention} has been removed from the authorized users list.", ephemeral=True)

        elif action == "Show":
            authorized_users = AuthorizedUsers.get_all(guild_id)
            if not authorized_users:
                return await interaction.response.send_message("📭 No authorized users found.", ephemeral=True)
            user_list = []
            for uid in authorized_users:
                member = interaction.guild.get_member(int(uid))
                user_list.append(f"- {member.mention if member else f'Unknown User ({uid})'}")
            description = "\n".join(user_list)
            embed = discord.Embed(title="✅ Authorized Users", description=description, color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
    
async def setup(bot: commands.Bot):
    await bot.add_cog(ManageAuth(bot))