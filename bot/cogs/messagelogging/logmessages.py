import discord
from discord.ext import commands
from models.messagelogger import MessageLogger

class MessageLoggingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_log_channel(self, guild: discord.Guild, is_bot: bool):
        settings = MessageLogger.get(guild.id)
        if not settings or not settings.message_logging_enabled:
            return None
        channel_id = settings.botlog_channel if is_bot else settings.humanlog_channel
        return guild.get_channel(int(channel_id)) if channel_id else None

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild is None or (message.author.bot and message.author.id == self.bot.user.id):
            return
        
        log_channel = self.get_log_channel(message.guild, message.author.bot)
        if not log_channel:
            return
        if message.channel == log_channel:
            return

        embed = discord.Embed(title="Message Deleted", color=discord.Color.red())
        embed.add_field(name="Author", value=message.author.mention, inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        content = message.content.strip() if message.content else ""
        if not content and message.stickers:
            content = f"Used sticker: {message.stickers[0].name}"
        
        embed.add_field(name="Content", value=content or "No content", inline=False)

        if message.attachments:
            if message.attachments[0].content_type.startswith(("image", "video")):
                embed.set_image(url=message.attachments[0].url)
            else:
                embed.add_field(
                    name="Attachment", value=message.attachments[0].url, inline=False
                )

        if message.embeds:
            embed.add_field(name="Embeds", value=f"{len(message.embeds)} embed(s)", inline=True)
        embed.timestamp = discord.utils.utcnow()
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.guild is None or (before.author.bot and before.author.id == self.bot.user.id):
            return
        if before.content == after.content and before.attachments == after.attachments:
            return

        log_channel = self.get_log_channel(before.guild, before.author.bot)
        if not log_channel:
            return
        if before.channel == log_channel:
            return

        embed = discord.Embed(title="Message Edited", color=discord.Color.orange())
        embed.add_field(name="Author", value=before.author.mention, inline=False)
        embed.add_field(name="Channel", value=before.channel.mention, inline=False)
        embed.add_field(name="Before", value=before.content or "No content", inline=False)
        embed.add_field(name="After", value=after.content or "No content", inline=False)
        embed.timestamp = before.edited_at or discord.utils.utcnow()
        await log_channel.send(embed=embed)
   

async def setup(bot: commands.Bot):
    await bot.add_cog(MessageLoggingCog(bot))