import discord
from discord.ext import commands
import typing
from utils.emotes import get_emoji
from resetdata.msgcount import reset_user_messages, reset_all_users_messages

class ResetMessages(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Reset Data"
    
    @commands.command(name="resetmessage", description = "Reset daily, weekly or monthly messages of an user or everyone.", aliases = ["resetmsg"])
    @commands.guild_only()
    async def reset_messages(self, ctx: commands.Context, duration: typing.Literal["daily", "weekly", "monthly", "daily-all", "weekly-all", "monthly-all"], user: discord.Member = None):
        async with ctx.typing():
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Administrator** permission to use this command."))
            duration = duration.strip().lower()
            guild_id = str(ctx.guild.id)
            if duration in ["daily", "weekly", "monthly"]:
                if user is None:
                    return await ctx.send(embed=discord.Embed(description=f"{get_emoji('blobcatred')} Please mention the user to reset their messages."))
                formatted_duration = f"{duration}-one"
                user_id = str(user.id)
                await reset_user_messages(formatted_duration,user_id, guild_id)
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('checkmark')} {duration.capitalize()} messages have been reset for {user.mention}."))
            await reset_all_users_messages(duration, guild_id)
            return await ctx.send(embed=discord.Embed(description=f"{get_emoji('checkmark')} {duration.capitalize()} messages have been reset for all users."))

    
async def setup(bot: commands.Bot):
    await bot.add_cog(ResetMessages(bot))