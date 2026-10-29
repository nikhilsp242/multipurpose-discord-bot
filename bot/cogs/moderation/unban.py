import discord
from discord.ext import commands
from utils.emotes import get_emoji

class Unban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"

    @commands.hybrid_command(name="unban", description="Unban a user from the server.")
    @discord.app_commands.describe(
        user="The user ID or mention to unban",
        reason="Reason for the unban (optional)"
    )
    @commands.guild_only()
    async def unban(self, ctx: commands.Context, user: discord.User, *, reason: str = "No reason provided"):
        checkmark = get_emoji("checkmark")
        crossmark = get_emoji("crossmark")
        blobcat = get_emoji("blobcatred")

        if not ctx.author.guild_permissions.ban_members:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Ban Members** permission."))

        user_id = user.id if user else None

        banned_users = [entry async for entry in ctx.guild.bans()]
        banned_entry = discord.utils.find(lambda entry: entry.user.id == user_id, banned_users)

        if banned_entry is None:
            return await ctx.send(embed=discord.Embed(description=f"{blobcat} This user is not banned in this server."))

        try:
            await ctx.guild.unban(banned_entry.user, reason=f"Unbanned by {ctx.author}")
            embed = discord.Embed(
                description=f"{checkmark} **{banned_entry.user}** has been unbanned.",
                color=discord.Color.green()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} I do not have permission to unban this user."))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} An error occurred: `{e}`"))

async def setup(bot: commands.Bot):
    await bot.add_cog(Unban(bot))
