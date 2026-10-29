import discord
from discord.ext import commands
import psutil
import time
from datetime import datetime, timezone
from utils.emotes import get_emoji

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()
        for command in self.get_commands():
            command.cog_category = "Utility"

    @commands.command(name="--ping", description="Show the bot's response time and system diagnostics.")
    async def ping(self, ctx: commands.Context):
        start = time.perf_counter()
        if ctx.interaction:
            await ctx.defer()
        else:
            async with ctx.typing():
                pass
        end = time.perf_counter()
        response_time = (end - start) * 1000

        latency = round(self.bot.latency * 1000)
        uptime_seconds = time.time() - self.start_time
        uptime_minutes = int(uptime_seconds // 60)
        uptime_hours = int(uptime_minutes // 60)
        uptime_days = int(uptime_hours // 24)

        process = psutil.Process()
        cpu_usage = process.cpu_percent(interval=0.5)
        mem_info = process.memory_full_info()
        memory_usage = mem_info.rss / (1024 ** 2)
        # memory_usage = psutil.virtual_memory().percent 
        # cpu_usage = psutil.cpu_percent(interval=0.5)
        disk_usage = psutil.disk_usage("/").percent
     
        total_users = len(set(self.bot.get_all_members()))
        total_guilds = len(self.bot.guilds)

        status = self.bot.status.name.capitalize()

        # Format days
        days_str = (
            f"{uptime_days} day{'s' if uptime_days != 1 else ''}"
            if uptime_days > 0
            else ""
        )

        # Format hours
        hours_str = (
            f"{uptime_hours % 24} hour{'s' if (uptime_hours % 24) != 1 else ''}"
            if uptime_hours > 0
            else ""
        )

        # Format minutes
        minutes_str = (
            f"{uptime_minutes % 60} minute{'s' if (uptime_minutes % 60) != 1 else ''}"
            if uptime_minutes > 0
            else ""
        )

        # Join the formatted components with commas and "and"
        components = [comp for comp in [days_str, hours_str, minutes_str] if comp]
        formatted_duration = (
            ", ".join(components[:-1])
            + (" and " if len(components) > 1 else "")
            + components[-1]
            if components
            else "Less than a minute"
        )

        heart = get_emoji("alive_heart")
        bolt = get_emoji("bolt")

        info = f"""
    # **My Info**
    ## ** {heart} I'm Alive !**
    > - **Status : {status}**
    > - **CPU Usage: {cpu_usage:.2f}%**
    > - **Memory Usage: {memory_usage:.1f} MB**
    > - **Disk Usage: {disk_usage}%**
    > - **WebSocket Latency: {latency} ms**
    > - **Response Time : {response_time:.0f} ms**
    > - **Uptime: {formatted_duration}**
    ### **{bolt} Scalability**
    > - **Servers: {total_guilds}**
    > - **Members: {total_users}**
    > - **Add me : [Install](https://discord.com/oauth2/authorize?client_id=1175726881111289856&permissions=1759218604441591&integration_type=0&scope=bot)**
    """
        embed = discord.Embed(
            description=info,
            timestamp=datetime.now(timezone.utc)
        )
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))
