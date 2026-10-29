import discord
from discord.ext import commands
from utils.emotes import get_emoji

class Kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"

    @commands.hybrid_command(name="kick", description="Kick a member from the server.")
    @discord.app_commands.describe(
        member="The member to kick",
        reason="Reason for the kick (optional)"
    )
    @commands.guild_only()
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        checkmark = get_emoji("checkmark")
        crossmark = get_emoji("crossmark")
        blobcat = get_emoji('blobcatred')
        if not ctx.author.guild_permissions.kick_members:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You do not have permission to **Kick Members**."))

        if member == ctx.author:
            return await ctx.send(embed=discord.Embed(description=f"{blobcat} You cannot kick yourself."))
        if member == ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description=f"{blobcat} Cannot kick the server owner."))
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You can only kick members below your top role."))

        try:
            await member.kick(reason=f'requested by {ctx.author.name}')
            embed=discord.Embed(description=f"{checkmark} {member.display_name} ({member.name}) has been kicked from the server.")
            embed.add_field(name="Reason", value=reason if reason else "Not provided")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} I do not have permission to kick this member."))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} An error occurred: `{e}`"))

async def setup(bot: commands.Bot):
    await bot.add_cog(Kick(bot))
