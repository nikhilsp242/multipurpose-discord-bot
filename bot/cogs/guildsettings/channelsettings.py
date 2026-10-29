import discord
from discord.ext import commands
from utils.emotes import get_emoji
from utils.getdata import mainChannelAvailable
from models.channels import Channel
import typing


class ChannelSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Settings"

    @commands.hybrid_command(name="set-main-channel", description = "Set a Main Channel for this guild", aliases = ["set-mc", "smc"])
    @commands.guild_only()
    @discord.app_commands.describe(channel="Select a text channel to mark it as main channel")
    async def set_main_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        if not ctx.author.guild_permissions.manage_channels:
            crossmark = get_emoji("crossmark")
            return await ctx.send(
                embed=discord.Embed(description=f"{crossmark} You need **Manage Channels** permission to use this command."),
                ephemeral=True if ctx.interaction else False
            )
        checkmark = get_emoji("checkmark")
        if not channel:
            channel = ctx.channel
        channel_id = str(channel.id)
        guild_id = str(ctx.guild.id)
        main_channel_available = mainChannelAvailable(guild_id)
        if main_channel_available and main_channel_available == channel_id:
            greenline =  get_emoji("greenline")
            return await ctx.send(embed=discord.Embed(description=f"**Target : {channel.mention}**\n{greenline} This channel is already set as main channel."))
        elif main_channel_available and main_channel_available != channel_id:
            current_main_channel = Channel.get(main_channel_available, guild_id)
            current_main_channel.is_main_channel = False
            current_main_channel.save()
            new_main_channel = Channel.get(channel_id, guild_id)
            new_main_channel.is_main_channel = True
            new_main_channel.name = channel.name
            new_main_channel.save()
            prev = ctx.guild.get_channel(int(main_channel_available))
            name = current_main_channel.name
            if not prev:
                current_main_channel.delete()
            return await ctx.send(embed=discord.Embed(description=f"**Target : {channel.mention}**\n {checkmark} Main channel changed from {prev.mention if prev else name} to {channel.mention}."))
        else:
            new_main_channel = Channel.get(channel_id, guild_id)
            new_main_channel.is_main_channel = True
            new_main_channel.name = channel.name
            new_main_channel.save()
            return await ctx.send(embed=discord.Embed(description=f"**Target : {channel.mention}**\n{checkmark} This channel has been set as main channel."))
    
    @commands.hybrid_command(name="xp-toggle", description = "Enable XP for a channel", aliases = ["xpt"])
    @commands.guild_only()
    @discord.app_commands.describe(
        channel="Select a channel to enable XP for it",
        toggle = "Enable or Disable xp for the channel")
    async def enable_xp(self, ctx: commands.Context, toggle:typing.Literal["enable", "disable"], channel: discord.abc.GuildChannel = None ):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_channels:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Manage Channels** permission to use this command."))
            checkmark = get_emoji("checkmark")
            blobcatred = get_emoji("blobcatred")
            if not channel:
                channel = ctx.channel
            channel_id = str(channel.id)
            guild_id = str(ctx.guild.id)
            channel_data = Channel.get(channel_id, guild_id)
            new_value = toggle == "enable"
            if channel_data.is_xp_channel == new_value:
                return await ctx.send(embed=discord.Embed(description=f"**Target : {channel.mention}**\n{blobcatred} XP is already {toggle}d in this channel."))
            channel_data.is_xp_channel = new_value
            channel_data.name = channel.name
            channel_data.save()
            return await ctx.send(embed=discord.Embed(description=f"**Target : {channel.mention}**\n{checkmark} XP has been **{toggle}d** in this channel."))
    
    @commands.hybrid_command(name="coins-toggle", description="Enable or disable coins for a channel", aliases=["coinst"])
    @commands.guild_only()
    @discord.app_commands.describe(channel="Channel to toggle coins for", toggle="Enable or Disable coins")
    async def toggle_coins(self, ctx: commands.Context, toggle: typing.Literal["enable", "disable"], channel: discord.abc.GuildChannel = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_channels:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Manage Channels** permission to use this command."))

            channel = channel or ctx.channel
            data = Channel.get(str(channel.id), str(ctx.guild.id))
            new_val = toggle == "enable"

            if data.is_coin_channel == new_val:
                return await ctx.send(embed=discord.Embed(description=f"**Target: {channel.mention}**\n{get_emoji('blobcatred')} Coins are already {toggle}d in this channel."))

            data.is_coin_channel = new_val
            data.name = channel.name
            data.save()
            return await ctx.send(embed=discord.Embed(description=f"**Target: {channel.mention}**\n{get_emoji('checkmark')} Coins have been **{toggle}d** in this channel."))
    
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.guild)
    @commands.hybrid_command(name="media-toggle", description="Enable or disable media (attachments) in a channel", aliases=["mediat", "media"])
    @commands.guild_only()
    @discord.app_commands.describe(channel="Channel to toggle media for", toggle="Enable or Disable media")
    async def toggle_media(self, ctx: commands.Context, toggle: typing.Literal["enable", "disable"], channel: discord.abc.GuildChannel = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            crossmark = get_emoji("crossmark")
            checkmark = get_emoji("checkmark")
            blobcatred = get_emoji("blobcatred")

            if not ctx.author.guild_permissions.manage_channels:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Manage Channels** permission to use this command."))

            channel = channel or ctx.channel
            bot_member = ctx.guild.me
            perms = channel.permissions_for(bot_member)

            if not perms.manage_channels:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} I need **Manage Channels** permission in {channel.mention} to modify its permissions."))

            data = Channel.get(str(channel.id), str(ctx.guild.id))
            new_val = toggle == "enable"

            if data.is_media_channel == new_val:
                return await ctx.send(embed=discord.Embed(description=f"**Target: {channel.mention}**\n{blobcatred} Media is already {toggle}d for this channel."))

            data.is_media_channel = new_val
            data.name = channel.name

            try:
                ow = channel.overwrites_for(ctx.guild.default_role)
                ow.attach_files = new_val
                await channel.set_permissions(ctx.guild.default_role, overwrite=ow)
                data.save()
                await ctx.send(embed=discord.Embed(description=f"**Target: {channel.mention}**\n{checkmark} Media has been **{toggle}d** for this channel."))
            except discord.Forbidden:
                await ctx.send(embed=discord.Embed(description=f"{crossmark} I don't have permission to modify overwrites in {channel.mention}."))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"{crossmark} An error occurred: {e}"))

        
async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelSettings(bot))