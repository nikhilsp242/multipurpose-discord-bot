import discord
from discord.ext import commands
from models.invitetrack import InviteTrack
from models.invites import Invites
from utils.accountage import get_account_age
import asyncio

class TrackInvites(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.missed_invites = {}
        self.vanity_uses = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        Invites.clear() # clears all records in the table and vacuumes to free up space
        count = 0
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            if InviteTrack.get(guild_id).invite_tracking_enabled :
                invites = await guild.invites()
                for invite in invites:
                    if invite.inviter:
                        inviter_id = str(invite.inviter.id)
                        Invites.save(guild_id, invite.code, inviter_id, invite.uses)
                        count += 1
                if guild.vanity_url_code:
                    vanity_invite = await guild.vanity_invite()
                    if vanity_invite:
                        self.vanity_uses[guild.id] = vanity_invite.uses
        print(f"✅ Saved {count} invites into the DB")


    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        try:
            guild = invite.guild
            guild_id = str(guild.id)
            invite_track = InviteTrack.get(guild_id)
            if not invite_track.invite_tracking_enabled:
                return
            if invite.inviter:
                inviter_id = invite.inviter.id
                Invites.save(guild_id, invite.code, inviter_id, invite.uses)
                invite_channel = guild.get_channel(int(invite_track.invitelog_channel))
                if invite_channel:
                    await invite_channel.send(embed=discord.Embed(description=f"Invite {invite.code} created by {invite.inviter.mention}"))
        except Exception as e:
            print(f"An error occurred in on_invite_create : {e}")
    
    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        try:
            guild = invite.guild
            guild_id = str(guild.id)
            invite_track = InviteTrack.get(guild_id)
            if not invite_track.invite_tracking_enabled:
                return
            inviter = Invites.get_one(guild_id, invite.code)
            self.missed_invites[invite.code] = inviter.inviter_id
            invite_channel = guild.get_channel(int(invite_track.invitelog_channel))
            if invite_channel:
                await invite_channel.send(embed=discord.Embed(description=f"Invite {invite.code} has been deleted or expired"))
            await asyncio.sleep(10)
            Invites.delete(guild_id, invite.code)
        except Exception as e:
            print(f"An error occurred in on_invite_delete : {e}")
        
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            guild = member.guild
            guild_id = str(guild.id)
            invite_track = InviteTrack.get(guild_id)
            if not invite_track.invite_tracking_enabled:
                return
            invite_channel_id = invite_track.invitelog_channel
            invite_channel = guild.get_channel(int(invite_channel_id))
            if member.bot and invite_channel:
                async for entry in guild.audit_logs(limit=10, action=discord.AuditLogAction.bot_add):
                    if entry.target.id == member.id:
                        adder = entry.user
                        embed=discord.Embed(title="Invite Tracking", description=f"Bot {member.mention} was added by {adder.mention}")
                        return
            stored_invites = Invites.get_all(guild_id)
            if not stored_invites:
                return
            fresh_invites = await guild.invites()
            fresh_invites = {invite.code : invite.uses for invite in fresh_invites if invite.inviter}
            inviter_id = None
            for invite in stored_invites:
                if invite.uses < fresh_invites.get(invite.invite_id, 0):
                    inviter_id = invite.inviter_id
                    Invites.save(guild_id, invite.invite_id, invite.inviter_id, invite.uses+1)
                    break
            if not inviter_id:
                for invite in stored_invites:
                    if self.missed_invites.get(invite.invite_id, 0):
                        inviter_id = invite.inviter_id
                        self.missed_invites.pop(invite.invite_id)
                        break
            if not inviter_id:
                if guild.vanity_url_code:
                    vanity_invite = await guild.vanity_invite()
                    if vanity_invite:
                        if vanity_invite.uses > self.vanity_uses.get(guild.id , 0):
                            inviter_id = "vanity"
                            self.vanity_uses[guild.id] = vanity_invite.uses
            if not invite_channel:
                return
            account_age = get_account_age(member)
            embed = discord.Embed(title="Invite Tracking")
            embed.add_field(name="Member Joined", value=f"{member.mention} ({member.name})", inline=False)
            embed.add_field(name="Account Age", value=account_age, inline=False)
            if not inviter_id:
                embed.add_field(name="Inviter", value="Could not figure out", inline=False)
            elif inviter_id == "vanity":
                embed.add_field(name="Join Method", value="Vanity URL", inline=False)
            else:
                inviter = guild.get_member(int(inviter_id))
                embed.add_field(name="Inviter", value=f"{inviter.mention} ({inviter.name})",inline=False)
            if invite_channel:
                await invite_channel.send(embed=embed)
        except Exception as e:
            print(f"An error occurred while tracking invites : {e}")     


async def setup(bot: commands.Bot):
    await bot.add_cog(TrackInvites(bot))           
