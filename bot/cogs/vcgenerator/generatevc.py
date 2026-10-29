import discord
from discord.ext import commands
from models.generatorchannels import GeneratorChannels
from utils.emotes import get_emoji
import asyncio

class VoiceGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}
        self.lock = asyncio.Lock()
        for command in self.get_commands():
            command.cog_category = "VC"

    @commands.hybrid_command(name="vctransfer", description="Transfer ownership of your temporary voice channel", aliases=["vtransfer", "vct"])
    @commands.guild_only()
    @discord.app_commands.describe(member="The member to transfer ownership to")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    async def vctransfer(self, ctx: commands.Context, member: discord.Member):
        if ctx.interaction: await ctx.defer()
        vc = ctx.author.voice.channel if ctx.author.voice else None
        crossmark = get_emoji("crossmark")
        checkmark = get_emoji("checkmark")
        blobcatred = get_emoji("blobcatred")

        if not vc:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You are not connected to any voice channel."), ephemeral=bool(ctx.interaction))

        if vc.id not in self.temp_channels:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} This VC is not a temporary channel."), ephemeral=bool(ctx.interaction))

        if self.temp_channels[vc.id] != ctx.author.id:
            return await ctx.send(embed=discord.Embed(description=f"{blobcatred} You are not the owner of this VC"))

        if member == ctx.author:
            return await ctx.send(embed=discord.Embed(description=f"{blobcatred} You are already the owner."))

        if member not in vc.members:
            return await ctx.send(embed=discord.Embed(description=f"{blobcatred} {member.mention} is not in your voice channel.", ephemeral=bool(ctx.interaction)))

        try:
            await vc.set_permissions(ctx.author, overwrite=None)
            overwrite = discord.PermissionOverwrite(manage_channels=True, manage_permissions=True, mute_members=True, move_members=True, deafen_members=True)
            await vc.set_permissions(member, overwrite=overwrite)

            self.temp_channels[vc.id] = member.id

            await vc.edit(name=f"{member.display_name}'s VC")

            await ctx.send(embed=discord.Embed(description=f"{checkmark} Ownership has been transferred to {member.mention}."))

        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"{crossmark} Error: {e}"))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild_id = str(member.guild.id)

        if after.channel and await self.is_generator(after.channel, guild_id) and not member.bot:
            await self.create_temp_channel(member, after.channel)
        
        if before.channel and before.channel.id in self.temp_channels:
            await self.handle_temp_channel(before.channel)
        
        if after.channel and after.channel.id in self.temp_channels:
            await self.handle_temp_channel(after.channel)
        
    
    async def create_temp_channel(self, member: discord.Member, generator_channel: discord.VoiceChannel):
        guild = member.guild
        category = generator_channel.category

        temp_channel = await guild.create_voice_channel(
            name=f"{member.global_name or member.name}'s VC",
            category=category
        )
        await member.move_to(temp_channel)

        await temp_channel.set_permissions(
            member,
            overwrite=discord.PermissionOverwrite(
                manage_channels=True,
                manage_permissions=True,
                mute_members=True,
                move_members=True,
                deafen_members=True
            )
        )
        self.temp_channels[temp_channel.id] = member.id
    
    async def handle_temp_channel(self, channel: discord.VoiceChannel):
        async with self.lock:
            await asyncio.sleep(1.5)
            members = channel.members
            owner_id = self.temp_channels.get(channel.id)

            if not members:
                del self.temp_channels[channel.id]
                await channel.delete()
                return

            if owner_id not in [m.id for m in members]:
                eligible_members = [m for m in members if not m.bot and m.id != owner_id]
                new_owner = eligible_members[0] if eligible_members else None
                if eligible_members:
                    await channel.set_permissions(new_owner, manage_channels=True, manage_permissions=True, mute_members=True, move_members=True, deafen_members=True)
                    await asyncio.sleep(0.5)
                self.temp_channels[channel.id] = new_owner.id if new_owner else None
                name = (new_owner.global_name or new_owner.name) if new_owner else "None"
                await channel.edit(name=f"{name}'s VC")
        
        await self.cleanup_stale_permissions(channel, members)

    async def cleanup_stale_permissions(self, channel: discord.VoiceChannel, current_members):
        """Remove overrides for users no longer in the VC"""
        all_overwrites = channel.overwrites
        current_ids = {m.id for m in current_members}

        for target, overwrite in all_overwrites.items():
            if isinstance(target, discord.Member) and target.id not in current_ids:
                await channel.set_permissions(target, overwrite=None)

    async def is_generator(self, channel: discord.VoiceChannel, guild_id):
        channel_id = str(channel.id)
        generator_channel = GeneratorChannels.get(channel_id, guild_id)
        return generator_channel 

async def setup(bot:commands.Bot):
    await bot.add_cog(VoiceGenerator(bot))