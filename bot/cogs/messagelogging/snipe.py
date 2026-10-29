import discord
from discord.ext import commands
from models.messagelogger import MessageLogger
from utils.emotes import get_emoji

def is_owner_guild(ctx: commands.Context):
    return ctx.guild and str(ctx.guild.id) == "1183064183646982164"

class Snipe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"

    @commands.command(name="snipe", description="Snipe deleted messages in a channel.")
    @commands.check(is_owner_guild)
    async def snipe(self, ctx: commands.Context, amount: int = 1, channel: discord.abc.GuildChannel=None):
        count = max(1, min(amount, 10))  
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_messages:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} You need **Manage Messages** permission to use this command."))
            guild = ctx.guild
            guild_id = str(guild.id)
            settings = MessageLogger.get(guild_id)
            if not settings.message_logging_enabled:
                return await ctx.send("Message logging is not enabled on this server.")

            log_channel_id = settings.humanlog_channel
            if not log_channel_id:
                return await ctx.send("No human log channel is configured.")
            
            log_channel = guild.get_channel(int(log_channel_id))
            if not log_channel:
                return await ctx.send("Log channel not found.")

            if not channel:
                channel = ctx.channel
            sniped = []
            async for msg in log_channel.history(limit=200):
                if not msg.embeds:
                    continue
                embed = msg.embeds[0]
                if embed.title != "Message Deleted" and embed.title != "Message Edited":
                    continue
                for field in embed.fields:
                    if field.name == "Channel" and field.value == channel.mention:
                        sniped.append(embed)
                        if len(sniped) >= count:
                            break
                if len(sniped) >= count:
                    break

            if not sniped:
                return await ctx.send("No recently deleted/edited messages found for this channel.")

            for embed in reversed(sniped): 
                await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Snipe(bot))
