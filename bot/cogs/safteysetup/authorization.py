import discord
from discord.ext import commands
from models.authorizedusers import AuthorizedUsers

class Authorization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            guild = member.guild
            if guild.id != 1183064183646982164:
                return
            async for entry in guild.audit_logs(limit=10, action=discord.AuditLogAction.bot_add):
                if entry.target.id == member.id:
                    user = entry.user
                    user_id = str(user.id)
                    guild_id = str(guild.id)
                    if not AuthorizedUsers.get_one(user_id, guild_id):
                        await member.ban(reason=f'This bot was added my an unathorized user ({user.name})')

async def setup(bot: commands.Bot):
    await bot.add_cog(Authorization(bot))

