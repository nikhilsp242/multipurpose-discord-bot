import discord
from discord.ext import commands
from datetime import datetime , timezone
from utils.assignroles import add_level_role
from models.userstats import UserStats
from models.levelup import LevelUpConfig
from utils.emotes import get_emoji
from utils.time_formating import format_time
from config import xpPerMin

vc_sessions = {}

class VcLeveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return
        if before.channel is None and after.channel is not None: 
            print(f"{member} joined {after.channel}")
            vc_sessions[member.id] = datetime.now(timezone.utc)
        
        elif before.channel is not None and after.channel is None:
            join_time = vc_sessions.pop(member.id, None)
            print(f"{member} left {before.channel}")
            if join_time:
                duration = ((datetime.now(timezone.utc) - join_time).total_seconds())
                print(int(duration))
                await self.handle_vc_xp(member, int(duration))

    async def handle_vc_xp(self, member: discord.Member, duration: int):
        if duration <= 0:
            return
        user_id = str(member.id)
        guild_id = str(member.guild.id)
        userstats = UserStats.get_one(user_id, guild_id)
        userstats.vc_time += duration
        guildsettings= LevelUpConfig.get(guild_id)
        try:
            xp_increase = (duration * xpPerMin) * (guildsettings.booster_xp_multiplier if member.premium_since else 1)  
            if guildsettings.vc_levelup_enabled:
                userstats.xp += xp_increase
                levelup_channel_id = guildsettings.levelup_channel
                levelup_channel = member.guild.get_channel(int(levelup_channel_id))
                level = await add_level_role(member, userstats.xp, userstats.level, levelup_channel)
                if level > userstats.level:
                    userstats.level = level
                    
            time_spent, milestone = get_milestone(userstats.vc_time , userstats.milestone)
            if milestone > userstats.milestone:
                userstats.milestone = milestone
                if guildsettings.vc_levelup_enabled and guildsettings.levelup_channel:
                    lvl_channel = member.guild.get_channel(int(guildsettings.levelup_channel))
                    vc = get_emoji("vc")
                    immortal = get_emoji("immortal")
                    embed = discord.Embed(
                        title="New Milestone Reached",
                        description=f"{vc} You've spent over **`{time_spent}` minutes** in voice channels! That's like **{format_time(time_spent)}**.\n{immortal} Your XP increased by **`{xp_increase}`** in your last session."
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                    await lvl_channel.send(f"{member.mention}", embed=embed)

            userstats.save()
        except Exception as e:
            print(e)



def get_milestone(duration, milestone):
    milestones = [
        (50000, 25),
        (40000, 24),
        (30000, 23),
        (25000, 22),
        (20000, 21),
        (15000, 20),
        (10000, 19),
        (9000, 18),
        (8000, 17),
        (7000, 16),
        (6000, 15),
        (5000, 14),
        (4000, 13),
        (3000, 12),
        (2000, 11),
        (1000, 10),
        (900, 9),
        (800, 8),
        (700, 7),
        (600, 6),
        (500, 5),
        (400, 4),
        (300, 3),
        (200, 2),
        (100, 1),
    ]

    for required_duration, milestone_number in milestones:
        if duration >= required_duration and milestone < milestone_number:
            return required_duration, milestone_number
    return duration, milestone

    
    

async def setup(bot :commands.Bot):
    await bot.add_cog(VcLeveling(bot))