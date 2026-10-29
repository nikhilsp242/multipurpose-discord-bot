import discord
from discord.ext import commands, tasks
from datetime import datetime
import asyncio
import pytz
from resetdata.msgcount import reset_messages
from cogs.musicrec.musicrecommendation import send_daily_recommendations

ist = pytz.timezone('Asia/Kolkata')

class StartUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.synced = False
        self.routine_calls.start()
    
    def cog_unload(self):
        self.routine_calls.cancel()
    
    @tasks.loop(minutes=1)
    async def routine_calls(self):
        now = datetime.now(ist)
        if now.hour == 0 and now.minute == 0:
            if now.day == 1:
                await reset_messages("monthly-all")
            elif now.weekday() == 0:
                await reset_messages("weekly-all")
            else:
                await reset_messages("daily-all")
            try:
                await send_daily_recommendations()
            except Exception as e:
                print
            await asyncio.sleep(60)
        if now.hour == 12 and now.minute == 0:
            await send_daily_recommendations()
            await asyncio.sleep(60)

    @routine_calls.before_loop
    async def before_routine(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.synced:
            try:
                await self.bot.tree.sync()
                guild = discord.Object(id=1175730830371455016)
                await self.bot.tree.sync(guild=guild)
                self.synced = True
                print("✅ Slash Commands Synced")
            except Exception as e:
                print(e)
        print(f"Logged in as {self.bot.user.name} - {self.bot.user.id}")
        # slash_commands = self.bot.tree.get_commands()
        # print(f"Total commands synced: {len(slash_commands)} + 2")

async def setup(bot: commands.Bot):
    await bot.add_cog(StartUp(bot))