import discord
from discord.ext import commands
from utils import ids

my_guild_id = ids.my_guild_id
server_mute_role = ids.server_mute_role
quarantine_role = ids.quarantine_role

class SetupChannels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        guild = channel.guild
        if guild.id != my_guild_id:
            return
        mute_role = discord.utils.get(guild.roles, id=server_mute_role)
        punishment_role = discord.utils.get(guild.roles, id=quarantine_role)

        if not mute_role:
            print("Mute role not found.")
            return

        if not punishment_role:
            print("Punishment role not found.")
            return

        mute_overwrite = discord.PermissionOverwrite()
        mute_overwrite.send_messages = False

        punishment_overwrite = discord.PermissionOverwrite()
        punishment_overwrite.view_channel = False

        try:
            await channel.set_permissions(mute_role, overwrite=mute_overwrite)
            await channel.set_permissions(punishment_role, overwrite=punishment_overwrite)
        except Exception as e:
            pass
    
async def setup(bot: commands.Bot):
    await bot.add_cog(SetupChannels(bot))
    