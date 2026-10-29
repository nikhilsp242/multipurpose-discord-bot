import discord
from discord.ext import commands
from models.userstats import UserStats
from utils.getdata import mainChannelAvailable
from utils.time_formating import format_time

class UserProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Stats"

    @commands.hybrid_command(name="profile", description = "View all the stats of an user", aliases = ["pf"])
    @commands.guild_only()
    @discord.app_commands.describe(user = "Select user to view their profile")
    async def profile(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                await ctx.send(embed=discord.Embed(description="This profile menu is only for human members"))
                return
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            user_stats = UserStats.get_one(user_id=user_id,guild_id=guild_id)
            if not user_stats:
                await ctx.send(embed=discord.Embed(description=f"{user.name} does not have any stats in this server"))
                return
            embed = discord.Embed(
                title=f"{user.display_name}'s Profile",
            )
            embed.add_field(name="User", value=user.mention,inline=True)
            embed.add_field(name="User Name", value=user.name, inline=True)
            embed.add_field(name="Highest Role", value=user.top_role.mention, inline=True)
            embed.add_field(name="Level", value=f"`{user_stats.level}`", inline=True)
            embed.add_field(name="Reputation", value=user_stats.reputation, inline=True)
            embed.add_field(name="XP", value=user_stats.xp, inline=True)
            embed.add_field(name="Balance", value=user_stats.balance, inline=True)
            embed.add_field(name="Total Messages", value=user_stats.total_messages,inline=True)
            if mainChannelAvailable(guild_id):
                embed.add_field(name="Messages in Main Channel", value=user_stats.main_channel_messages, inline=True)
            embed.add_field(name="Replies Received", value=user_stats.replies_received, inline=True)
            embed.add_field(name="Attachments Sent", value=user_stats.total_attachments, inline=True)
            embed.add_field(name="VC Time", value=format_time(user_stats.vc_time), inline=True )
            embed.set_thumbnail(url=f"{user.avatar.url if user.avatar else user.default_avatar.url}")

            await ctx.send(embed=embed)
        

async def setup(bot: commands.Bot):
    await bot.add_cog(UserProfile(bot))