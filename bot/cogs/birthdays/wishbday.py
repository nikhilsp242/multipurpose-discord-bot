import discord
from discord.ext import commands , tasks
from models.birthdays import Birthdays
from models.channels import Channel
from models.todaybday import TodayBirthdays
from models.roles import Roles
from datetime import datetime , timezone
import pytz
import time
import asyncio


class WishUsers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_started = False
        self.birthday_lock = asyncio.Lock()
    
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.birthday_started:
            self.birthday_task.start()
            self.birthday_started = True
            print("✅ Birthday task started")
    
    @tasks.loop(minutes=1)
    async def birthday_task(self):
        async with self.birthday_lock:
            try:
                await self.check_birthdays()
                await self.remove_bday_role()
            except Exception as e:
                print(f"❌ Error in birthday_task: {e}")

    
    @birthday_task.before_loop
    async def before_birthday_task(self):
        await self.bot.wait_until_ready()   
    
    async def check_birthdays(self):
        date  = get_today_timezone()
        if not date:
            return
        day , month, time_zone = date
        birthdays = Birthdays.get_all(day, month, time_zone)
        if not birthdays:
            return
        for birthday in birthdays:
            guild_id = birthday.guild_id
            user_id = birthday.user_id
            birthday_channel_id = Channel.get_channel(guild_id, "isBdayChannel").channel_id
            if birthday_channel_id:
                guild = self.bot.get_guild(int(guild_id))
                if guild:
                    user = guild.get_member(int(user_id))
                    bday_channel = guild.get_channel(int(birthday_channel_id))
                    current_year =  datetime.now(pytz.timezone(birthday.timezone)).year
                    age = current_year - birthday.year if birthday.year else None
                    wish = f"Happy birthday {user.mention} 🎉. You turned {age} today!" if age else f"Happy birthday {user.mention} 🎉."
                    embed = discord.Embed(
                        title=f"🎂 {user.display_name}'s Birthday",
                        description=wish
                    )
                    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
                    embed.set_footer(text=f"Wished as per {time_zone} timezone")
                    await bday_channel.send(user.mention, embed=embed)
                    bday_role_id = Roles.get_role(guild_id, "is_bday_role").role_id
                    if bday_role_id:
                        bday_role = guild.get_role(int(bday_role_id))
                        if bday_role and bday_role not in user.roles:
                            await user.add_roles(bday_role, reason="Birthday")
                            today_bday = TodayBirthdays.get_one(user_id, guild_id)
                            ts = datetime.now(timezone.utc).timestamp()
                            today_bday.role_id = bday_role_id
                            today_bday.time_stamp = ts
                            today_bday.save()

    
    async def remove_bday_role(self):
        today_birthdays = TodayBirthdays.get_all()
        if not today_birthdays:
            return
        now = time.time()
        for birthday in today_birthdays:
            if now - birthday.time_stamp >= 86400:
                user_id = birthday.user_id
                role_id = birthday.role_id
                guild_id = birthday.guild_id
                guild = self.bot.get_guild(int(guild_id))
                user = guild.get_member(int(user_id))
                role = guild.get_role(int(role_id))
                if guild and user and role and role in user.roles:
                    await user.remove_roles(role, reason="Birthday Over")
                birthday.delete()
                
    

def get_today_timezone():
    timezones = ["UTC", "America/New_York", "America/Los_Angeles", "Europe/London", "Europe/Paris", "Asia/Kolkata", "Asia/Karachi", "Asia/Dubai", 
    "Asia/Tokyo", "Asia/Singapore", "Asia/Jakarta", "Asia/Seoul", "Asia/Shanghai", "Australia/Sydney", "Africa/Cairo", "Europe/Moscow", "America/Sao_Paulo",
    "America/Mexico_City", "Africa/Nairobi", "Pacific/Auckland"]
    for timezone in timezones:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        if current_time.hour == 0 and current_time.minute == 0:
            print(timezone)
            return current_time.day, current_time.month, timezone
    

async def setup(bot: commands.Bot):
    await bot.add_cog(WishUsers(bot))