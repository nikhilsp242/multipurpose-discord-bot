import discord
from discord.ext import commands
from models.afkusers import AfkUsers
import time
from utils.time_formating import format_afk_duration

class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"
    
    @commands.hybrid_command(name="afk", description="Set yourself as AFK with an optional reason.")
    @commands.guild_only()
    async def set_afk(self, ctx: commands.Context,* , reason=None):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        AfkUsers.save(user_id, guild_id, reason, time.time())
        response = f"{ctx.author.mention}, you are now AFK! **| Reason :** {reason}" if reason else f"{ctx.author.mention}, you are now AFK!"
        if ctx.interaction:
            return await ctx.send(response, allowed_mentions=discord.AllowedMentions(users=False, roles=False,everyone=False), ephemeral=True)
        return await ctx.reply(response, allowed_mentions=discord.AllowedMentions(users=False, roles=False,everyone=False), mention_author=False)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        ctx = await self.bot.get_context(message)
        if ctx.valid and ctx.command and ctx.command.name == "afk":
            return
        user_id = str(message.author.id)
        guild_id = str(message.guild.id)
        afk = AfkUsers.get(user_id, guild_id)
        if afk:
            elapsed = time.time() - afk.since_timestamp
            formatted_duration = format_afk_duration(elapsed)
            afk.delete()
            await message.reply(f"Welcome back {message.author.mention}! **|** You were AFK for **{formatted_duration}**",allowed_mentions=discord.AllowedMentions(users=False), mention_author=False)


        mentioned_users = {user.id for user in message.mentions if user != message.author}
        if not mentioned_users:
            return

        notified = set()
        for userid in mentioned_users:
            afk = AfkUsers.get(str(userid), guild_id)
            if afk and userid not in notified:
                elapsed = time.time() - afk.since_timestamp
                formatted_duration = format_afk_duration(elapsed)
                user = message.guild.get_member(userid)
                response = f"{user.mention} is currently AFK for {formatted_duration} **| Reason :** {afk.reason}" if afk.reason else f"{user.mention} is currently AFK for {formatted_duration}"
                await message.reply(response, allowed_mentions=discord.AllowedMentions(users=False, roles=False,everyone=False), mention_author=False)
                notified.add(userid)

async def setup(bot: commands.Bot):
    await bot.add_cog(AFK(bot))