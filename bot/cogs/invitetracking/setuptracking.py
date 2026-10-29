import discord
from discord.ext import commands
from models.invitetrack import InviteTrack
from models.invites import Invites
from utils.emotes import get_emoji

class SetUpTracking(commands.Cog):
    def __init__(self, bot):
        self.bot =  bot
        for command in self.get_commands():
            command.cog_category = "Settings"
    
    @commands.hybrid_command(name="setup-invite-tracking", description="Set up invite tracking for this guild", aliases = ["setupinv", "enableinv"])
    @commands.guild_only()
    @discord.app_commands.describe(invite_channel="Channel for logging invites")
    async def setup_invite_tracking(self, ctx: commands.Context, invite_channel: discord.TextChannel):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_guild:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Manage Guild** permission to use this command."))

            bot_member = ctx.guild.me
            if not bot_member.guild_permissions.manage_guild:
                return await ctx.send(embed=discord.Embed(
                    description=f"{crossmark} I need **Manage Guild** permission to access vanity invites."
                ))
            
            guild_id = str(ctx.guild.id)
            inv_tracking = InviteTrack.get(guild_id)

            if inv_tracking.invite_tracking_enabled:
                blobcatred = get_emoji("blobcatred")
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} Invite tracking is already enabled for this guild."))

            permissions = invite_channel.permissions_for(bot_member)
            required_perms = ["send_messages", "embed_links", "view_channel"]
            missing = [perm.replace("_", " ").title() for perm in required_perms if not getattr(permissions, perm)]

            if missing:
                return await ctx.send(embed=discord.Embed(
                    description=f"{crossmark} I am missing the following permissions in {invite_channel.mention}: {', '.join(missing)}."
                ))
            
            inv_tracking.invite_tracking_enabled = True
            inv_tracking.invitelog_channel = invite_channel.id
            inv_tracking.save()
            invites = await ctx.guild.invites()
            for invite in invites:
                if invite.inviter:
                    inviter_id = str(invite.inviter.id)
                    Invites.save(guild_id, invite.code, inviter_id, invite.uses)
            checkmark = get_emoji("checkmark")
            return await ctx.send(embed=discord.Embed(description=f"{checkmark} Successfully enabled invite tracking."))
    
    @commands.hybrid_command(name="disable-invite-tracking", description="Disable invite tracking for this guild", aliases=["disableinv"])
    @commands.guild_only()
    async def disable_invite_tracking(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_guild:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Manage Guild** permission to use this command."))
            guild_id = str(ctx.guild.id)
            inv_tracking = InviteTrack.get(guild_id)
            if not inv_tracking.invite_tracking_enabled:
                blobcat= get_emoji("blobcatred")
                return await ctx.send(embed=discord.Embed(description=f"{blobcat} Invite tracking is not enabled in this guild."))
            inv_tracking.invite_tracking_enabled = False
            inv_tracking.save()
            invites = Invites.get_all(guild_id)
            if invites:
                Invites.delete_all(guild_id)
            checkmark = get_emoji("checkmark")
            return await ctx.send(embed=discord.Embed(description=f"{checkmark} Successfully disabled invite tracking."))

async def setup(bot: commands.Bot):
    await bot.add_cog(SetUpTracking(bot))