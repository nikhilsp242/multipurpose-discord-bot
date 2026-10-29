import discord
from discord.ext import commands, tasks
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta , timezone
from models.authorizedusers import AuthorizedUsers
from utils import ids

guild_id = ids.my_guild_id
bypass_role_id = ids.nuke_bypass_role_id
log_channel_id = ids.log_channel_id

class AntiNuke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def check_and_ban(self, guild: discord.Guild, action: discord.AuditLogAction):
        try:
            async for entry in guild.audit_logs(
                limit=1, action=action
            ):
                executor = entry.user

                if not executor.bot or executor == guild.me:
                    return  
                member = guild.get_member(executor.id)
                if member is None:
                    return  

                bypass_role = guild.get_role(bypass_role_id)
                if bypass_role and bypass_role in member.roles:
                    return  

                await guild.ban(member, reason="Antinuke: Bot created/deleted channel without bypass role.")
                embed = discord.Embed(description=f"{member.name} has been banned for channel creation/deletion.")
                await guild.owner.send(embed=embed)
        except Exception as e:
            print(f"Error in antinuke: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        if channel.guild.id != guild_id:
            return
        await self.check_and_ban(channel.guild, discord.AuditLogAction.channel_create)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if channel.guild.id != guild_id:
            return
        await self.check_and_ban(channel.guild, discord.AuditLogAction.channel_delete)


class AntiNukeMassBanKick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.action_counts = defaultdict(list)
        self.threshold = 3
        self.timeframe = timedelta(seconds=10)
        self.cleanup_task.start()

    def cog_unload(self):
        self.cleanup_task.cancel()

    @tasks.loop(seconds=30)
    async def cleanup_task(self):
        now = datetime.now(timezone.utc)
        for executor_id in list(self.action_counts):
            self.action_counts[executor_id] = [
                t for t in self.action_counts[executor_id]
                if now - t < self.timeframe
            ]
            if not self.action_counts[executor_id]:
                del self.action_counts[executor_id]

    async def handle_mass_action(self, guild: discord.Guild, action_type: discord.AuditLogAction):
        await asyncio.sleep(1)
        try:
            async for entry in guild.audit_logs(limit=1, action=action_type):
                executor = entry.user
                if executor == guild.me or executor is None:
                    return

                authorized_users = AuthorizedUsers.get_all(str(guild_id))
                if executor.id in authorized_users:
                    return  # Authorized user, skip

                member = guild.get_member(executor.id)
                if not member:
                    return

                now = datetime.now(timezone.utc)
                self.action_counts[executor.id].append(now)

                recent_actions = [
                    t for t in self.action_counts[executor.id]
                    if now - t < self.timeframe
                ]

                if len(recent_actions) >= self.threshold:
                    await guild.ban(member, reason="Antinuke: Mass bans/kicks detected.")
                    embed = discord.Embed(
                        description=f"🚨 **Antinuke:** Banned {member.mention} for performing {len(recent_actions)} {action_type.name}s within {self.timeframe.seconds} seconds."
                    )
                    log_channel = guild.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    if guild.owner:
                        try:
                            await guild.owner.send(embed=embed)
                        except discord.Forbidden:
                            pass
                    self.action_counts[executor.id].clear()
        except Exception as e:
            print(f"[Antinuke MassBanKick Error]: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.id != guild_id:
            return
        await self.handle_mass_action(member.guild, discord.AuditLogAction.ban)
        await self.handle_mass_action(member.guild, discord.AuditLogAction.kick)




async def setup(bot: commands.Bot):
    await bot.add_cog(AntiNuke(bot))
    await bot.add_cog(AntiNukeMassBanKick(bot))