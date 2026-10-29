import discord
from discord.ext import commands
from models.messagelogger import MessageLogger
import typing
from utils.emotes import get_emoji

class SetupLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Settings"

    @commands.hybrid_command(name="message-logging", description="Setup message logging for this guild")
    @commands.guild_only()
    @discord.app_commands.describe(
        toggle="Enable or disable this setting.",
        humanlog_channel = "Channel to log messages of human members",
        botlog_channel="Channel to log bot messages"
    )
    async def message_logging(self, ctx: commands.Context, toggle: typing.Literal["enable", "disable"], humanlog_channel: discord.TextChannel=None, botlog_channel: discord.TextChannel=None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("crossmark")} You need **Administrator** permission to you use this command"))
            
            guild_id = str(ctx.guild.id)
            message_logging = MessageLogger.get(guild_id)
            if toggle == "disable":
                message_logging.message_logging_enabled = False
                message_logging.save()
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("checkmark")} Message logging has been disabled for this guild."))
            elif not humanlog_channel and not botlog_channel:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} Please provide both the channels."))
            bot_member = ctx.guild.me  
            human_perms = humanlog_channel.permissions_for(bot_member)
            bot_perms = botlog_channel.permissions_for(bot_member)
            if not human_perms.send_messages:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} I do not have permission to send messages in {humanlog_channel.mention}"))

            if not bot_perms.send_messages:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} I do not have permission to send messages in {botlog_channel.mention}"))
            message_logging.message_logging_enabled = True
            message_logging.humanlog_channel = humanlog_channel.id
            message_logging.botlog_channel = botlog_channel.id
            message_logging.save()
            return await ctx.send(embed=discord.Embed(description=f"{get_emoji("checkmark")} Message logging has been enabled for this guild."))
    
async def setup(bot: commands.Bot):
    await bot.add_cog(SetupLogger(bot))