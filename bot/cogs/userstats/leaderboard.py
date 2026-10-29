import discord
from discord.ext import commands
from models.userstats import UserStats
from models.messagecount import MessageCount
from utils.getdata import mainChannelAvailable
from utils.emotes import get_emoji
from utils.time_formating import format_time
import typing


class LeaderboardView(discord.ui.View):
    def __init__(self, ctx, author, stat, entries, emoji:str, per_page=25):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.author = author
        self.entries = entries
        self.stat = stat
        self.emoji = emoji
        self.per_page = per_page
        self.page = 0
        self.message = None
    
        self.update_buttons()

    async def send_embed(self):
        embed = self.create_embed()
        if self.ctx.interaction:
            await self.ctx.interaction.edit_original_response(embed=embed, view=self)
            self.message = await self.ctx.interaction.original_response()
        else:
            self.message = await self.ctx.send(embed=embed, view=self)
        
    
    def create_embed(self):
        stat = self.stat.replace("_", " ").title()
        embed = discord.Embed(title=f"Leaderboard for {stat}")
        start = self.page * self.per_page
        end = start + self.per_page
        page_entries = self.entries[start:end]

        if not page_entries:
            embed.description = "No entries found."
            return embed
        chat = get_emoji(self.emoji)
        description = ""
        for i, user_stat in enumerate(page_entries, start=1):
            user = self.ctx.guild.get_member(int(user_stat.user_id))
            value = getattr(user_stat, self.stat)
            if self.stat == "vc_time":
                value = format_time(value)

            if user:
                description += f"{i + start}. {user.display_name} ({user.mention}) - {value} {chat}\n"
            else:
                description += f"{i + start}. Unknown User {user_stat.user_id} - {value} {chat}\n"

        embed.description = description.strip()
        embed.set_footer(text=f"Page {self.page + 1} / {((len(self.entries) - 1) // self.per_page) + 1}")
        return embed
    
    def update_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == "prev_button":
                    child.disabled = self.page == 0
                elif child.custom_id == "next_button":
                    child.disabled = (self.page + 1) * self.per_page >= len(self.entries)

    
    @discord.ui.button(label="◀️ Prev", style=discord.ButtonStyle.secondary, custom_id="prev_button")
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message(f"{get_emoji("blobcatred")} This leaderboard menu is controlled by {self.author.mention}", ephemeral=True)
            return
        if self.page > 0:
            self.page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
    
    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.secondary , custom_id="next_button")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message(f"{get_emoji("blobcatred")} This leaderboard menu is controlled by {self.author.mention}", ephemeral=True)
            return
        if (self.page + 1) * self.per_page < len(self.entries):
            self.page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
    
    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if self.message:
            await self.message.edit(view=self)  # ✅ reflect timeout disable
   

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Leaderboard"

    @commands.hybrid_command(name="leaderboard", description="View the server's leaderboards of various stats", aliases=["lb"])
    @commands.guild_only()
    @discord.app_commands.describe(stat="The stat to view the leaderboard for.")
    async def leaderboard(self, ctx: commands.Context, *, stat: typing.Literal["xp", "balance", "messages", "replies", "attachments", "vc time"] = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            STAT_ALIASES = {
                "xp": "xp",
                "balance": "balance",
                "messages": "total_messages",
                "replies": "replies_received",
                "attachments": "total_attachments",
                "vc time": "vc_time"
            }
            if not stat:
                stat = "messages"
            else:
                stat = stat.lower()

            if stat not in STAT_ALIASES:
                return await ctx.send(embed=discord.Embed(
                    title=f"❌ Invalid Stat",
                    description=f"{stat}`.\nValid options: `{', '.join(STAT_ALIASES.keys())}`"
                    )
                )
            stat = STAT_ALIASES[stat]
            alluserstats = UserStats.get_all(ctx.guild.id)
            if not alluserstats:
                return await ctx.send(embed=discord.Embed(description="No user stats found for this server."))
            STAT_EMOJI = {
                "xp": "immortal",
                "balance": "ecoin",
                "total_messages": "chat",
                "replies_received": "ping",
                "total_attachments": "attachments",
                "vc_time": "vc"
            }

            alluserstats.sort(key=lambda x: getattr(x, stat), reverse=True)
            view = LeaderboardView(ctx, ctx.author, stat, alluserstats, STAT_EMOJI[stat],  per_page=25)
            await view.send_embed()


class MessageStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Leaderboard"
        
    @commands.hybrid_command(name="message-leaderboard", description = "View daily , weekly or monthly leaderboard for messages", aliases = ["lbm", "mlb"])
    @commands.guild_only()
    @discord.app_commands.describe(duration = "The duration for which you want to view the message stats")
    async def messagestats(self, ctx: commands.Context, *, duration: typing.Literal["daily", "weekly", "monthly", "daily in main channel", "weekly in main channel", "monthly in main channel"] = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            DURATION_ALIASES = {
                "daily": "daily_messages",
                "weekly": "weekly_messages",
                "monthly": "monthly_messages",
                "daily in main channel": "daily_main_channel_messages",
                "weekly in main channel": "weekly_main_channel_messages",
                "monthly in main channel": "monthly_main_channel_messages",
            }
            if not duration:
                duration = "daily"
            else:
                duration = duration.lower()
            crossmark = get_emoji("crossmark")

            if duration not in DURATION_ALIASES:
                return await ctx.send(embed=discord.Embed(
                    title=f"❌ Invalid Duration" ,
                    description=f"`{duration}`.\nValid options: `{', '.join(DURATION_ALIASES.keys())}`"
                    )
                )
            guild_id = str(ctx.guild.id)
            duration = DURATION_ALIASES[duration]
            if duration in {"daily_main_channel_messages", "weekly_main_channel_messages", "monthly_main_channel_messages"} and not mainChannelAvailable(guild_id):
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} Main Channel is not set for this guild"))

            messagestats = MessageCount.get_all(ctx.guild.id)
            if not messagestats:
                return await ctx.send(embed=discord.Embed(description="No user stats found for this server."))
            messagestats.sort(key=lambda x: getattr(x, duration), reverse=True)
            view = LeaderboardView(ctx, ctx.author, duration, messagestats, "chat", per_page=25)
            await view.send_embed()

async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))
    await bot.add_cog(MessageStats(bot))

