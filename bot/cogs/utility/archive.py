import discord
from discord.ext import commands
from utils.emotes import get_emoji
from models.archivedchannels import ArchivedChannel

class Archive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"
    
    @commands.hybrid_command(name="archive", description="Archive a channel that is not currently in use", aliases=["arch"])
    @commands.guild_only()
    @discord.app_commands.describe(channel="Select a channel to archive")
    async def archive(self, ctx: commands.Context, channel: discord.abc.GuildChannel=None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_channels:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Manage Channels** permission to use this command."))
            if not channel:
                channel = ctx.channel
            if isinstance(channel, discord.CategoryChannel):
                return await ctx.send(embed=discord.Embed(description=f"**Target : {channel.name}**\n{get_emoji('blobcatred')} Cannot archive a category channel."))

            try:
                channel_id = str(channel.id)
                category_id = str(channel.category_id)
                guild_id = str(ctx.guild.id)
                archived_category = discord.utils.get(ctx.guild.categories, name="Archived-Channels")
                if archived_category is None:
                    archived_category = await ctx.guild.create_category("Archived-Channels")
                await channel.edit(category=archived_category)
                await channel.set_permissions(ctx.guild.default_role, view_channel=False)
                ArchivedChannel.save(channel_id, guild_id, category_id)
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('checkmark')} {channel.mention} has been archived"))
            except Exception as e:
                await ctx.send(
                    embed=discord.Embed(description=f"{get_emoji('crossmark')} Failed to archive: {e}")
                )

    @commands.hybrid_command(name="unarchive", description="Unarchive a channel that is archived.", aliases=["unarch"])
    @commands.guild_only()
    @discord.app_commands.describe(channel="Select a channel to unarchive")
    async def unarchive(self, ctx: commands.Context, channel: discord.abc.GuildChannel=None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_channels:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Manage Channels** permission to use this command."))
            if not channel:
                channel = ctx.channel
            if isinstance(channel, discord.CategoryChannel):
                return await ctx.send(embed=discord.Embed(description=f"**Target : {channel.name}**\n{get_emoji('blobcatred')} Cannot unarchive a category channel."))

            try:
                channel_id = str(channel.id)
                guild_id = str(ctx.guild.id)
                archived_channel = ArchivedChannel.get(channel_id, guild_id)
                category = ctx.guild.get_channel(int(archived_channel.category_id))
                await channel.edit(category=category)
                await channel.set_permissions(ctx.guild.default_role, view_channel=True)
                archived_channel.delete()
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('checkmark')} {channel.mention} has been unarchived"))
            except Exception as e:
                await ctx.send(
                    embed=discord.Embed(description=f"{get_emoji('crossmark')} Failed to unarchive: {e}")
                )
            
async def setup(bot: commands.Bot):
    await bot.add_cog(Archive(bot))       