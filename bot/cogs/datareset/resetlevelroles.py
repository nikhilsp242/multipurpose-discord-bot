import discord
from discord.ext import commands
from models.levelroles import LevelRole
from utils.emotes import get_emoji

class ResetLevelRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Reset Data"
    
    @commands.command(name="removelevelrole")
    @commands.guild_only()
    async def resetlevelrolesdata(self, ctx: commands.Context, level: int):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Administrator** permission to use this command."))
        guild_id = str(ctx.guild.id)
        LevelRole.delete_by_level(guild_id, level)
        return await ctx.send(embed=discord.Embed(description=f"{get_emoji('checkmark')} Deleted data for level {level}."))

async def setup(bot: commands.Bot):
    await bot.add_cog(ResetLevelRoles(bot))