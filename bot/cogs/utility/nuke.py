import discord
from discord.ext import commands
from utils.emotes import get_emoji
from discord.ui import View, Button
import typing


class ConfirmNuke(View):
    def __init__(self, channel: discord.abc.GuildChannel, ctx:commands.Context):
        super().__init__(timeout=60)
        self.channel = channel
        self.ctx = ctx
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You cannot interact with this confirmation.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction : discord.Interaction, button : Button):
        embed = discord.Embed(title="Nuking Cancelled" , description=f'The nuking of {self.channel.mention} has been cancelled.', color=discord.Color.lighter_grey())
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction : discord.Interaction, button : Button):
        if isinstance(self.channel, (discord.TextChannel , discord.VoiceChannel)):
            try:
                category = self.channel.category if not isinstance(self.channel, discord.CategoryChannel) else None
                new_channel = await self.channel.clone(reason="Nuking Channel")
                if category:
                    await new_channel.edit(category=category, reason="Nuking Channel")
                await self.channel.delete(reason="Nuking Channel")
                await new_channel.send(embed = discord.Embed(description=f'Nuked by {self.ctx.author.mention}'))
                if self.channel != self.ctx.channel:
                    await interaction.response.edit_message(embed=discord.Embed(description=f"{get_emoji('checkmark')} {new_channel.mention} has been nuked!"), view=None)
            except discord.Forbidden:
                await interaction.response.edit_message(embed=discord.Embed(description=f"{get_emoji('nyaSob')} I don't have permission to manage channels."), view=None)
            except discord.HTTPException as e:
                await interaction.response.edit_message(embed=discord.Embed(description=f"{get_emoji('crossmark')} Failed to nuke the channel: `{e}`"), view=None)

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass


class Nuke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"
    
    @commands.hybrid_command(name="nuke", description="Nuke a channel (delete and clone)")
    @commands.guild_only()
    @discord.app_commands.describe(channel="Select a channel to nuke")
    async def nuke(self, ctx: commands.Context, channel: typing.Union[discord.TextChannel, discord.VoiceChannel]=None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_channels:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("crossmark")} You need **Manage Channels** permission to use this command."))
            if not channel:
                channel = ctx.channel
            embed = discord.Embed(title="Confirm Nuke", description=f"Are you sure you want to nuke {channel.mention}", color=discord.Color.red())
            view = ConfirmNuke(channel, ctx)
            view.message = await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Nuke(bot))