import discord
from discord.ext import commands
from utils.emotes import get_emoji

class ChannelLock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"

    @commands.hybrid_command(name="lock", description="Lock a channel to prevent sending messages.")
    @commands.guild_only()
    @discord.app_commands.describe(
        channel="Channel to lock (leave empty to lock current)",
        role="Role to lock (leave empty to lock @everyone)")
    async def lock(self, ctx: commands.Context, channel: discord.abc.GuildChannel = None, role: discord.Role=None):
        if ctx.interaction: await ctx.defer()
        crossmark = get_emoji('crossmark')
        checkmark = get_emoji('checkmark')
        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Manage Channels** permission to use this command."))

        channel = channel or ctx.channel
        role = role or ctx.guild.default_role

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False
        try:
            await channel.set_permissions(role, overwrite=overwrite)
            await ctx.send(embed=discord.Embed(description=f"{checkmark} {channel.mention} has been **locked** for {role.mention}."))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} Failed to lock {channel.mention} for {role.mention}. Error: {e}"))

    @commands.hybrid_command(name="unlock", description="Unlock a channel to allow sending messages.")
    @commands.guild_only()
    @discord.app_commands.describe(
        channel="Channel to unlock (leave empty to unlock current)",
        role="Role to unlock (leave empty to unlock @everyone)")
    async def unlock(self, ctx: commands.Context, channel: discord.abc.GuildChannel = None, role: discord.Role = None):
        if ctx.interaction: await ctx.defer()
        crossmark = get_emoji('crossmark')
        checkmark = get_emoji('checkmark')
        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Manage Channels** permission to use this command."))

        channel = channel or ctx.channel
        role = role or ctx.guild.default_role

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = None  # reset send_messages to default

        # Check if other permissions are set
        other_perms = any(
            value is not None and perm != "send_messages"
            for perm, value in dict(overwrite).items()
        )  
        try:
            if not other_perms:
                # Remove overwrite entirely if no other permissions are set
                await channel.set_permissions(role, overwrite=None)
                msg = f"{checkmark} {channel.mention} has been unlocked for {role.mention}."
            else:
                await channel.set_permissions(role, overwrite=overwrite)
                msg = f"{checkmark} {channel.mention} has been unlocked for {role.mention}."

            await ctx.send(embed=discord.Embed(description=msg))

        except Exception as e:
            await ctx.send(embed=discord.Embed(
                description=f"{crossmark} Failed to unlock {channel.mention} for {role.mention}. Error: {e}"
            ))
    
    @commands.hybrid_command(name="lockall", description="Lock the server by disabling Send Messages for @everyone.")
    @commands.guild_only()
    async def lockall(self, ctx: commands.Context):
        if ctx.interaction: await ctx.defer()
        crossmark = get_emoji('crossmark')
        checkmark = get_emoji('checkmark')
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(
                description=f"{crossmark} You need **Administrator** permission to use this command."
            ))

        role = ctx.guild.default_role  # @everyone
        try:
            perms = role.permissions
            perms.update(send_messages=False)
            await role.edit(permissions=perms, reason=f"Lockall invoked by {ctx.author}")
            await ctx.send(embed=discord.Embed(
                description=f"{checkmark} Locked the server: only members without bypass roles cannot send messages."
            ))
        except Exception as e:
            await ctx.send(embed=discord.Embed(
                description=f"{crossmark} Failed to lock the server. Error: {e}"
            ))

    @commands.hybrid_command(name="unlockall", description="Unlock the server by enabling Send Messages for @everyone.")
    @commands.guild_only()
    async def unlockall(self, ctx: commands.Context):
        if ctx.interaction: await ctx.defer()
        crossmark = get_emoji('crossmark')
        checkmark = get_emoji('checkmark')
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(
                description=f"{crossmark} You need **Administrator** permission to use this command."
            ))

        role = ctx.guild.default_role  # @everyone
        try:
            perms = role.permissions
            perms.update(send_messages=True)
            await role.edit(permissions=perms, reason=f"Unlockall invoked by {ctx.author}")
            await ctx.send(embed=discord.Embed(
                description=f"{checkmark} Unlocked the server: members can send messages again."
            ))
        except Exception as e:
            await ctx.send(embed=discord.Embed(
                description=f"{crossmark} Failed to unlock the server. Error: {e}"
            ))        

async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelLock(bot))
