import discord
from discord.ext import commands
from utils.emotes import get_emoji
from datetime import timedelta, datetime
import re

def parse_duration(duration_str):
    """Parses duration strings like '1h30m' into seconds."""
    pattern = r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
    match = re.fullmatch(pattern, duration_str.strip().lower())
    if not match:
        return None
    days, hours, minutes, seconds = match.groups(default="0")
    total_seconds = (
        int(days) * 86400 +
        int(hours) * 3600 +
        int(minutes) * 60 +
        int(seconds)
    )
    return total_seconds if total_seconds > 0 else None

class Timeout(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"

    @commands.hybrid_command(name="timeout", description="Timeout a member for a specific duration.", aliases=["tmo"])
    @discord.app_commands.describe(
        member="The member to timeout",
        duration="Duration (e.g., 1h30m, 2d, 30m)",
        reason="Reason for timeout (optional)"
    )
    @commands.guild_only()
    async def timeout(self, ctx: commands.Context, member: discord.Member, duration: str, *, reason: str = None):
        crossmark = get_emoji("crossmark")
        if not ctx.author.guild_permissions.moderate_members:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Moderate Members** permission to use this command."))
        
        checkmark = get_emoji("checkmark")

        if member == ctx.author:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You cannot timeout yourself."))
        if member.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} Cannot timeout administrators."))
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You can only timeout members below your top role."))
        duration_seconds = parse_duration(duration)
        if duration_seconds is None:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} Invalid duration format. Use formats like `1h`, `30m`, `2d`, `15s`."))

        try:
            timeout_until = discord.utils.utcnow() + timedelta(seconds=duration_seconds)
            await member.edit(timed_out_until=timeout_until, reason=f"requested by {ctx.author.name}")

            formatted = f"<t:{int(timeout_until.timestamp())}:F>"
            embed=discord.Embed(description=f"{checkmark} {member.mention} has been timed out until {formatted}.")
            embed.add_field(name="Reason", value=reason if reason else "Not provided")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} I do not have permission to timeout this member."))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} An error occurred: `{e}`"))

    @commands.hybrid_command(name="untimeout", description="Remove timeout from a member.", aliases=["rtmo", "remove-timeout"])
    @discord.app_commands.describe(
        member="The member to remove timeout from"
    )
    @commands.guild_only()
    async def untimeout(self, ctx: commands.Context, member: discord.Member):
        crossmark = get_emoji("crossmark")
        blobcat = get_emoji('blobcatred')
        if not ctx.author.guild_permissions.moderate_members:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Moderate Members** permission to use this command."))
        if member.timed_out_until is None:
            return await ctx.send(embed=discord.Embed(description=f"{blobcat} This member is not currently timed out."))
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You can only remove timeout from members below your top role."))
        checkmark = get_emoji("checkmark")
        try:
            await member.edit(timed_out_until=None, reason=f'requested by {ctx.author.name}')
            await ctx.send(embed=discord.Embed(description=f"{checkmark} Removed timeout from {member.mention}."))
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} I do not have permission to remove the timeout for this member."))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} An error occurred: `{e}`"))

async def setup(bot: commands.Bot):
    await bot.add_cog(Timeout(bot))
