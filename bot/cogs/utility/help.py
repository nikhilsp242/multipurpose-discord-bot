import discord
from discord.ext import commands
from utils.emotes import get_emoji


class HelpDropdown(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.categories_dict = get_commands_by_category(bot)
        for category, commands in self.categories_dict.items():
            self.categories_dict[category] = [
                cmd for cmd in commands if cmd.name not in {"snipe", "load", "unload", "reload", "listcogs", "run", "bumprole", "grant", "deny", "permguide", "quarantine", "release", "recommend", "listallrec", "listrec", "upcoming-songs", "restoredata"}
            ]
        self.categories = sorted(self.categories_dict.keys())
        options = [
            discord.SelectOption(label=category, description=f"View commands in {category}")
            for category in self.categories
        ]
        super().__init__(placeholder="Select a command category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        commands = self.categories_dict[category]

        sorted_commands = sorted(commands, key=lambda cmd: cmd.name.lower())

        embed = discord.Embed(title=f"{category} Commands")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Use help <command> to get more information about a command.")

        for cmd in sorted_commands:
            embed.add_field(name=f"`{cmd.name}`", value=cmd.description or "No description", inline=False)

        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=120)
        self.bot = bot
        self.dropdown = HelpDropdown(bot)
        self.add_item(self.dropdown)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                child.disabled = True
        try:
            await self.message.edit(view=self)
        except Exception:
            pass

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"

    @commands.hybrid_command(name="help", description="Show all commands or info about a specific command")
    @commands.guild_only()
    async def help(self, ctx: commands.Context, *, command_name: str = None):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if command_name:
                command = self.bot.get_command(command_name)
                if not command:
                    return
                    # crossmark = get_emoji("crossmark")
                    # return await ctx.send(embed=discord.Embed(description=f"{crossmark} Command `{command_name}` not found."), delete_after=5)
                embed = discord.Embed(
                    title=f"Help for - {command.name}",
                    description=command.description or command.help or "No description"
                )
                embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                if command.aliases:
                    embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
                if command.signature:
                    embed.add_field(name="Usage", value=f"`{ctx.prefix}{command.name} {command.signature}`", inline=False)
                return await ctx.send(embed=embed)

            embed = discord.Embed(
                title="Command Help",
                description="Select a category from the dropdown below to see available commands."
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            view = HelpView(self.bot)
            sent = await ctx.send(embed=embed, view=view)
            view.message = sent

def get_commands_by_category(bot: commands.Bot):
    categories = {}
    for command in bot.commands:
        if command.hidden:
            continue
        category = getattr(command, "cog_category", command.cog_name or "Uncategorized")
        categories.setdefault(category, []).append(command)
    return categories

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))