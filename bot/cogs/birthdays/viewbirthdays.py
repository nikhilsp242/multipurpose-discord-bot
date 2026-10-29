import discord
from discord.ext import commands
from models.birthdays import Birthdays
from discord.ui import View, Button
from datetime import datetime
from utils.emotes import get_emoji

class BirthdayListView(View):
    def __init__(self, ctx, author, entries, per_page=10):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.author = author
        self.entries = entries
        self.per_page = per_page
        self.page = 0
        self.message = None
        self.update_buttons()

    def update_buttons(self):
        self.prev.disabled = self.page == 0
        self.next.disabled = (self.page + 1) * self.per_page >= len(self.entries)

    def create_embed(self):
        embed = discord.Embed(title="🎂 Birthday List", color=discord.Color.blurple())
        start = self.page * self.per_page
        end = start + self.per_page
        page_entries = self.entries[start:end]

        for i, birthday in enumerate(page_entries, start=start + 1):
            user = self.ctx.guild.get_member(int(birthday.user_id))
            name = user.display_name if user else f"Unknown ({birthday.user_id})"
            bday = f"{birthday.day}/{birthday.month}"
            if birthday.year != 0:
                age = datetime.now().year - birthday.year
                bday += f" ({age} yrs)"
            embed.add_field(name=f"{i}. {name}", value=bday, inline=False)

        embed.set_footer(text=f"Page {self.page + 1} / {((len(self.entries) - 1) // self.per_page) + 1}")
        return embed

    async def update_message(self, interaction):
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="◀️ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message(f"{get_emoji("blobcatred")} This birthday menu is controlled by {self.author.mention}", ephemeral=True)
            return
        if self.page > 0:
            self.page -= 1
            await self.update_message(interaction)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message(f"{get_emoji("blobcatred")} This birthday menu is controlled by {self.author.mention}", ephemeral=True)
            return
        if (self.page + 1) * self.per_page < len(self.entries):
            self.page += 1
            await self.update_message(interaction)

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass

class ViewBirthdays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Birthday"

    @commands.hybrid_command(name="birthday-list", description="Show list of all birthdays in the server", aliases=["bdaylist", "bdays", "birthdays"])
    @commands.guild_only()
    async def birthday_list(self, ctx: commands.Context):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            guild_id = str(ctx.guild.id)
            birthdays = Birthdays.get_guild_bdays(guild_id)
            if not birthdays:
                return await ctx.send("No birthdays have been added for this server yet.", ephemeral=bool(ctx.interaction))

            view = BirthdayListView(ctx, ctx.author, birthdays, per_page=10)
            embed = view.create_embed()

            if ctx.interaction:
                await ctx.interaction.edit_original_response(embed=embed, view=view)
                view.message = await ctx.interaction.original_response()
            else:
                view.message = await ctx.send(embed=embed, view=view)
    

    @commands.hybrid_command(name="check-birthday", description="Check birthday of an user in this server", aliases=["bday", "birthday"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select a user to get their birthday")
    async def get_birthday(self, ctx: commands.Context, user: discord.Member=None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            birthday = Birthdays.get_one(user_id, guild_id)
            blobcatr = get_emoji("blobcatred")
            blobcatb = get_emoji("blobcatblue")
            if not birthday.day:
                return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{blobcatr} This user has not added their birthday."),ephemeral=bool(ctx.interaction))
            bday = f"{birthday.day}/{birthday.month}/{birthday.year}" if birthday.year else f"{birthday.day}/{birthday.month}"
            return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{blobcatb} **Birthday : {bday}**"),ephemeral=bool(ctx.interaction))
        
async def setup(bot: commands.Bot):
    await bot.add_cog(ViewBirthdays(bot))