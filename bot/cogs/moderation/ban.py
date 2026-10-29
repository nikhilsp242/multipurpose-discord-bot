import discord
from discord.ext import commands
from utils.emotes import get_emoji

class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"

    @commands.hybrid_command(name="ban", description="Ban a member from the server.")
    @discord.app_commands.describe(
        user="The member to ban",
        reason="Reason for the ban (optional)"
    )
    @commands.guild_only()
    async def ban(self, ctx: commands.Context, user: discord.User, *, reason: str = None):
        checkmark = get_emoji("checkmark")
        crossmark = get_emoji("crossmark")
        blobcat = get_emoji('blobcatred')

        if not ctx.author.guild_permissions.ban_members:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You do not have permission to **Ban Members**."))

        if not ctx.guild.me.guild_permissions.ban_members:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} I do not have permission to **Ban Members**."))
        member = ctx.guild.get_member(user.id)

        if user.id == ctx.author.id:
            return await ctx.send(embed=discord.Embed(description=f"{blobcat} You cannot ban yourself."))
        if user.id == ctx.guild.owner.id:
            return await ctx.send(embed=discord.Embed(description=f"{blobcat} Cannot ban the server owner."))
        if member:
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You can only ban members below your top role."))
            if member.top_role >= ctx.guild.me.top_role:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} I cannot ban this member as they are above or equal to my top role."))

        try:
            await ctx.guild.ban(user, reason=f"requested by {ctx.author.name}")
            embed = discord.Embed(
                description=f"{checkmark} {user.name} has been banned from the server."
            )
            embed.add_field(name="Reason", value=reason if reason else "Not provided")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} I do not have permission to ban this member."))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} An error occurred: `{e}`"))

async def setup(bot: commands.Bot):
    await bot.add_cog(Ban(bot))
