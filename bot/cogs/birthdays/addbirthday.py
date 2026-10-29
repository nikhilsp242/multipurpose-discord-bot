from discord.ext import commands
import discord
from utils.emotes import get_emoji
from models.birthdays import Birthdays
from datetime import datetime
import typing


class AddBirthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Birthday"
    
    
    @commands.hybrid_command(name="birthday-add", description="Add your birthday", aliases=["addbday", "setbday"])
    @commands.guild_only()
    @discord.app_commands.describe(
        day="Add day",
        month="Add month",
        year="Add year",
        timezone="Add your timezone (you will be wished accordingly)",
        user="Select user"
    )
    async def birthday_add(
        self,
        ctx: commands.Context, 
        day: int,
        month: typing.Literal["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        year: int = None,
        timezone: typing.Literal["UTC", "America/New_York", "America/Los_Angeles", "Europe/London", "Europe/Paris", "Asia/Kolkata", "Asia/Karachi", "Asia/Dubai", 
    "Asia/Tokyo", "Asia/Singapore", "Asia/Jakarta", "Asia/Seoul", "Asia/Shanghai", "Australia/Sydney", "Africa/Cairo", "Europe/Moscow", "America/Sao_Paulo",
    "America/Mexico_City", "Africa/Nairobi", "Pacific/Auckland"] = "Asia/Kolkata",
        user: discord.Member = None
    ):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            crossmark = get_emoji("crossmark")
            blobcat = get_emoji("blobcatred")
            checkmark = get_emoji("checkmark")

            if user != ctx.author and not ctx.author.guild_permissions.manage_guild:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You are not allowed to add another user's birthday."))

            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            month = month_dict[month]
            if not year:
                year = 0  # Handle the case where no year is provided (default to 0)
            if not validDate(day, month, year):
                return await ctx.send(embed=discord.Embed(description=f"{blobcat} You have entered an invalid date. Please try again."))
            
            # Save birthday data
            birthday = Birthdays.get_one(user_id, guild_id)
            birthday.day = day
            birthday.month = month
            birthday.year = year
            birthday.timezone = timezone if timezone else "Asia/Kolkata"
            birthday.save()
            date = f"**{day}/{month}/{year}**" if year != 0 else f"**{day}/{month}**"
            return await ctx.send(embed=discord.Embed(description=f"{checkmark} **{user.display_name}'s** birthday has been set to {date} with time zone - **{birthday.timezone}**."))
    

def validDate(day: int, month: int, year: int) -> bool:
    # Check if year is valid (considering leap years)
    if year != 0:
        if day > 31 or month < 1 or month > 12 or day < 1:
            return False
        current_year = datetime.now().year
        if year < 1900 or year > current_year:
            return False
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 1 <= day <= 31
    elif month in [4, 6, 9, 11]:
        return 1 <= day <= 30
    elif month == 2:
        # Leap year check
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            return 1 <= day <= 29
        else:
            return 1 <= day <= 28
    else:
        return False

month_dict = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

async def setup(bot: commands.Bot):
    await bot.add_cog(AddBirthday(bot))
