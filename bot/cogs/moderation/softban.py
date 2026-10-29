import discord
from discord.ext import commands
from utils.emotes import get_emoji

class Softban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"

    @commands.hybrid_command(name="softban", description="Softban a user (ban, delete messages, unban instantly).")
    @discord.app_commands.describe(
        member="The member to softban",
        reason="Reason for the softban (optional)"
    )
    @commands.guild_only()
    async def softban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            checkmark = get_emoji("checkmark")
            crossmark = get_emoji("crossmark")
            blobcat = get_emoji("blobcatred")

            if not ctx.author.guild_permissions.ban_members:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Ban Members** permission."))

            if member == ctx.author:
                return await ctx.send(embed=discord.Embed(description=f"{blobcat} You cannot softban yourself."))
            if member == ctx.guild.owner:
                return await ctx.send(embed=discord.Embed(description=f"{blobcat} Cannot softban the server owner."))
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You can only softban members below your top role."))
            if member.top_role >= ctx.guild.me.top_role:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} I do not have permission to softban this member."))

            try:
                await member.ban(delete_message_days=1, reason=f"requested by {ctx.author.name}")
                await ctx.guild.unban(member, reason=f"Softban removal by {ctx.author}")
                description=f"{checkmark} **{member.display_name}** ({member.name}) has been **banned**\n{checkmark} Cleared messages sent by **{member.display_name} in the past 24hours**\n{checkmark} Unbanned **{member.display_name}**" if not member.bot else f"{checkmark} **{member.display_name}** ({member.name}) has been **banned**\n{checkmark} Unbanned **{member.display_name}**"
                embed = discord.Embed(
                    description=description,
                    color=discord.Color.orange()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                await ctx.send(embed=embed)

            except discord.Forbidden:
                await ctx.send(embed=discord.Embed(description=f"{crossmark} I do not have permission to softban this user."))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"{crossmark} An error occurred: `{e}`"))

async def setup(bot: commands.Bot):
    await bot.add_cog(Softban(bot))
