import discord
from discord.ext import commands
from utils.emotes import get_emoji

class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"
    
    @commands.hybrid_command(name="purge", description="Clear messages in a channel")
    @commands.guild_only()
    @discord.app_commands.describe(amount="Number of messages to clear", user="Clear messages of a particular user")
    async def purge(self, ctx: commands.Context, amount: int , user: discord.Member=None):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_messages:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("crossmark")} You need **Manage Messages** permission to use this command"))
            if user:
                deleted = await ctx.channel.purge(limit=min(amount+1, 1000), check=lambda m: m.author.id == user.id)
                if ctx.interaction:
                    try: 
                        return await ctx.send(embed=discord.Embed(description=f"{get_emoji("checkmark")} Cleared {len(deleted)} message{"s" if len(deleted) > 1 else ""} sent by {user.mention}"), ephemeral=True)
                    except Exception:
                        pass
                return await ctx.channel.send(embed=discord.Embed(description=f"{get_emoji("checkmark")} Cleared {len(deleted)} message{"s" if len(deleted) > 1 else ""} sent by {user.mention}"), delete_after=10)
 
            deleted = await ctx.channel.purge(limit=min(amount+1,1000))
            if ctx.interaction:
                try:
                    return await ctx.send(embed=discord.Embed(description=f"{get_emoji("checkmark")} Cleared {len(deleted)-1} message{"s" if len(deleted)-1 > 1 else ""}"),ephemeral=True)
                except Exception:
                    pass
            await ctx.channel.send(embed=discord.Embed(description=f"{get_emoji("checkmark")} Cleared {len(deleted)-1} message{"s" if len(deleted)-1 > 1 else ""}"),delete_after=10)

    @commands.command(name="clear", description="Clear messages of a particular target", aliases=["clr"])
    @commands.guild_only()
    async def clear(self, ctx: commands.Context,* , target: str=None):
        if not ctx.author.guild_permissions.manage_messages:
            return await ctx.send(embed=discord.Embed(description=f"{get_emoji("crossmark")} You need **Manage Messages** permission to use this command"))
        if not target:
            return await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} Please specify a target (bots, humans)"))
        deleted = []
        async with ctx.typing():
            target = target.lower().strip()

            if target in {"bot", "b", "bots"}:
                deleted = await ctx.channel.purge(limit=200, check=lambda m: m.author.bot)
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("checkmark")} Cleared {len(deleted)} bot message{'s' if len(deleted) != 1 else ''}."),delete_after=10)

            elif target in {"h", "human", "humans"}:
                deleted = await ctx.channel.purge(limit=200, check=lambda m: not m.author.bot)
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("checkmark")} Cleared {len(deleted)-1} human message{'s' if len(deleted) != 1 else ''}."), delete_after=10)

            elif target == "till here":
                if not ctx.message.reference or not ctx.message.reference.resolved:
                    return await ctx.send(embed=discord.Embed(description=f"{get_emoji('blobcatred')} You need to tag a message."))

                target_msg = ctx.message.reference.resolved
                after_time = target_msg.created_at

                deleted = await ctx.channel.purge(
                    limit=200,
                    check=lambda m: m.created_at >= after_time
                )
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('checkmark')} Cleared {len(deleted)} message{'s' if len(deleted) != 1 else ''}."),delete_after=10)

            else:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} Invalid target. Use `bots`, `humans`, or `till here`."), delete_after=5)


async def setup(bot: commands.Bot):
    await bot.add_cog(Purge(bot))