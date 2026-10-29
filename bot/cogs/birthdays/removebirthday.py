from discord.ext import commands
import discord
from utils.emotes import get_emoji
from models.birthdays import Birthdays

class RemoveBirthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Birthday"

    @commands.hybrid_command(name="birthday-remove", description="Remove birthday of an user", aliases=["removebday", "rembday"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to remove their birthday")
    async def remove_bday(self, ctx: commands.Context, user: discord.Member=None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            crossmark = get_emoji("crossmark")
            blobcat = get_emoji("blobcatred")
            checkmark = get_emoji("checkmark")

            if user != ctx.author and not ctx.author.guild_permissions.manage_guild:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You are not allowed to remove another user's birthday."))

            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            birthday = Birthdays.get_one(user_id, guild_id)
            if not birthday.day:
                return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{blobcat} This user has not registered their birthday."))
            birthday.delete()
            return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{checkmark} This user's birthday has been deleted."))
    
async def setup(bot: commands.Bot):
    await bot.add_cog(RemoveBirthday(bot))