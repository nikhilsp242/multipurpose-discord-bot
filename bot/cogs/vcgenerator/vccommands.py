import discord
from discord.ext import commands
from utils.emotes import get_emoji
from utils.permissions import check_vc_permission

class VcCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "VC"
   

    @check_vc_permission('manage_channels')
    @commands.hybrid_command(name="vclimit", description = "Set a limit for voice channel", aliases = ["vlim", "vclim"])
    @commands.guild_only()
    @discord.app_commands.describe(
        limit="The number of users that are allowed to connect to the voice channel",
        channel="The voice channel that you want to limit"
        )
    async def limit_vc(self, ctx: commands.Context, limit: int=None, channel: discord.VoiceChannel=None):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            if channel is None:
                if isinstance(ctx.channel, discord.VoiceChannel):
                    channel = ctx.channel
                else:
                    crossmark = get_emoji("crossmark")
                    await ctx.send(embed=discord.Embed(description=f"{crossmark} This command is only for voice channels."), ephemeral=True if ctx.interaction else False)
                    return

            if limit is None:
                limit = len(channel.members)
            elif limit > 99 or limit <= 0:
                limit = 0
            await channel.edit(user_limit=limit)
            checkmark = get_emoji("checkmark")
            if limit == 0:
                await ctx.send(embed=discord.Embed(description=f'{checkmark} User limit for {channel.mention} has been removed.'), ephemeral=True if ctx.interaction else False)
            else:
                await ctx.send(embed=discord.Embed(description=f'{checkmark} User limit for {channel.mention} is set to **{limit}**.'), ephemeral=True if ctx.interaction else False)

    @check_vc_permission('manage_channels')
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vclock", description="Lock your voice channel", aliases=["vlock", "vcl"])
    @commands.guild_only()
    async def lock_vc(self, ctx: commands.Context):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            members = vc.members

            if len(members) > 50:
                return await ctx.send(embed=discord.Embed(description=f"⚠️ Too many users in the voice channel to apply individual overrides (limit: 50)."))
            
            default_overwrite = vc.overwrites_for(ctx.guild.default_role)
            default_overwrite.connect = False
            await vc.set_permissions(ctx.guild.default_role, overwrite=default_overwrite)

            for member in members:
                existing_overwrite = vc.overwrites_for(member)
                existing_overwrite.connect = True
                await vc.set_permissions(member, overwrite=existing_overwrite)

            checkmark = get_emoji("checkmark")
            await ctx.send(embed=discord.Embed(description=f"🔒 {vc.mention} is now **locked**. {checkmark}"))


    @check_vc_permission('manage_channels')
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vcunlock", description="Unlock your voice channel", aliases=["vunlock", "vcu"])
    @commands.guild_only()
    async def unlock_vc(self, ctx: commands.Context):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel

            default_overwrite = vc.overwrites_for(ctx.guild.default_role)
            default_overwrite.connect = None
            await vc.set_permissions(ctx.guild.default_role, overwrite=default_overwrite)

            for member in vc.members:
                existing_overwrite = vc.overwrites_for(member)
                existing_overwrite.connect = None
                await vc.set_permissions(member, overwrite=existing_overwrite)

            checkmark = get_emoji("checkmark")
            await ctx.send(embed=discord.Embed(description=f"🔓 {vc.mention} is now **unlocked**. {checkmark}"))
    
    @check_vc_permission("manage_channels")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vcban", description="Ban a user from your VC", aliases=["vban"])
    @commands.guild_only()
    @discord.app_commands.describe(member="Member to ban from your VC")
    async def vc_ban(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            checkmark = get_emoji("checkmark")
            blobcatred = get_emoji("blobcatred")
            if member == ctx.author:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} You cannot ban yourself."))
            if member.guild_permissions.administrator:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} Cannot ban administrators."))
            if member.voice and member.voice.channel == vc:
                await member.move_to(None)
            await vc.set_permissions(member, connect=False)
            await ctx.send(embed=discord.Embed(description=f"{checkmark} {member.mention} has been **banned** from {vc.mention}."))

    @check_vc_permission("manage_channels")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vckick", description="Kick a user from your VC", aliases=["vkick"])
    @commands.guild_only()
    @discord.app_commands.describe(member="Member to kick from your VC")
    async def vc_kick(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            crossmark = get_emoji("crossmark")
            checkmark = get_emoji("checkmark")
            if member.voice and member.voice.channel == vc:
                await member.move_to(None)
                await ctx.send(embed=discord.Embed(description=f"{checkmark} {member.mention} has been **kicked** from {vc.mention}."))
            else:
                await ctx.send(embed=discord.Embed(description=f"{crossmark} {member.mention} is not in your voice channel."))

    @check_vc_permission("manage_channels")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vcmute", description="Mute a user in your VC", aliases=["vmute"])
    @commands.guild_only()
    @discord.app_commands.describe(member="Member to mute in VC")
    async def vc_mute(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            crossmark = get_emoji("crossmark")
            checkmark = get_emoji("checkmark")
            if member.voice and member.voice.channel == vc:
                await member.edit(mute=True)
                await ctx.send(embed=discord.Embed(description=f"{checkmark} {member.mention} has been **server-muted** in {vc.mention}."))
            else:
                await ctx.send(embed=discord.Embed(description=f"{crossmark} {member.mention} is not in your voice channel."))

    @check_vc_permission("manage_channels")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vcdeafen", description="Deafen a user in your VC", aliases=["vdeafen"])
    @commands.guild_only()
    @discord.app_commands.describe(member="Member to deafen in VC")
    async def vc_deafen(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            crossmark = get_emoji("crossmark")
            checkmark = get_emoji("checkmark")
            if member.voice and member.voice.channel == vc:
                await member.edit(deafen=True)
                await ctx.send(embed=discord.Embed(description=f"{checkmark} {member.mention} has been **server-deafened** in {vc.mention}."))
            else:
                await ctx.send(embed=discord.Embed(description=f"{crossmark} {member.mention} is not in your voice channel."))

    @check_vc_permission("manage_channels")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vcunban", description="Unban a user from your VC", aliases=["vunban"])
    @commands.guild_only()
    @discord.app_commands.describe(member="Member to unban from your VC")
    async def vc_unban(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            checkmark = get_emoji("checkmark")
            await vc.set_permissions(member, overwrite=None)
            await ctx.send(embed=discord.Embed(description=f"{checkmark} {member.mention} has been **unbanned** from {vc.mention}."))

    @check_vc_permission("manage_channels")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vcunmute", description="Unmute a user in your VC", aliases=["vunmute"])
    @commands.guild_only()
    @discord.app_commands.describe(member="Member to unmute in VC")
    async def vc_unmute(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            crossmark = get_emoji("crossmark")
            checkmark = get_emoji("checkmark")
            if member.voice and member.voice.channel == vc:
                await member.edit(mute=False)
                await ctx.send(embed=discord.Embed(description=f"{checkmark} {member.mention} has been **unmuted** in {vc.mention}."))
            else:
                await ctx.send(embed=discord.Embed(description=f"{crossmark} {member.mention} is not in your voice channel."))

    @check_vc_permission("manage_channels")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vcundeafen", description="Undeafen a user in your VC", aliases=["vundeafen"])
    @commands.guild_only()
    @discord.app_commands.describe(member="Member to undeafen in VC")
    async def vc_undeafen(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            crossmark = get_emoji("crossmark")
            checkmark = get_emoji("checkmark")
            if member.voice and member.voice.channel == vc:
                await member.edit(deafen=False)
                await ctx.send(embed=discord.Embed(description=f"{checkmark} {member.mention} has been **undeafened** in {vc.mention}."))
            else:
                await ctx.send(embed=discord.Embed(description=f"{crossmark} {member.mention} is not in your voice channel."))
    
    @check_vc_permission("manage_channels")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vchide", description="Hide the voice channel", aliases=["vhide", "vch"])
    @commands.guild_only()
    @discord.app_commands.describe(member="Member to hide the voice channel from (leave blank to hide from everyone)")
    async def vc_hide(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            crossmark = get_emoji("crossmark")
            checkmark = get_emoji("checkmark")

            if member:
                if member == ctx.author:
                    return await ctx.send(embed=discord.Embed(description=f"{crossmark} You can't hide the voice channel from yourself."))
                await vc.set_permissions(member, view_channel=False)
                await ctx.send(embed=discord.Embed(description=f"{checkmark} {vc.mention} is now **hidden** from {member.mention}."))
            else:
                await vc.set_permissions(ctx.guild.default_role, view_channel=False)
                await ctx.send(embed=discord.Embed(description=f"{checkmark} {vc.mention} is now **hidden** from everyone."))

    @check_vc_permission("manage_channels")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vcunhide", description="Unhide the voice channel", aliases=["vunhide", "vcuh"])
    @commands.guild_only()
    @discord.app_commands.describe(member="Member to unhide the voice channel for (leave blank to unhide for everyone)")
    async def vc_unhide(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            checkmark = get_emoji("checkmark")

            if member:
                await vc.set_permissions(member, view_channel=True)
                await ctx.send(embed=discord.Embed(description=f"{checkmark} {vc.mention} is now **visible** to {member.mention}."))
            else:
                await vc.set_permissions(ctx.guild.default_role, view_channel=None)
                await ctx.send(embed=discord.Embed(description=f"{checkmark} {vc.mention} is now **visible** to everyone."))
    
    @check_vc_permission("manage_channels")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.hybrid_command(name="vcallow", description="Allow a user to join your locked VC", aliases=["vallow"])
    @commands.guild_only()
    @discord.app_commands.describe(member="Member to allow access to your VC")
    async def vc_allow(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            vc = ctx.author.voice.channel
            blobcatred = get_emoji("blobcatred")
            checkmark = get_emoji("checkmark")
            crossmark = get_emoji("crossmark")
            if member == ctx.author:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} You already have access to your own VC."))
            default_overwrite = vc.overwrites_for(ctx.guild.default_role)
            locked = default_overwrite.connect is False
            hidden = default_overwrite.view_channel is False

            if not locked and not hidden:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} Your voice channel is neither locked nor hidden. No need to allow access."))
            overwrite = vc.overwrites_for(member)
            if hidden:
                overwrite.view_channel = True
            if locked:
                overwrite.connect = True
            await vc.set_permissions(member, overwrite=overwrite)

            await ctx.send(embed=discord.Embed(description=f"{checkmark} {member.mention} has been **allowed** to join `{vc.mention}`."))


async def setup(bot: commands.Bot):
    await bot.add_cog(VcCommands(bot))
