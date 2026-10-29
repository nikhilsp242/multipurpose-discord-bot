import discord
from discord.ext import commands
from models.generatorchannels import GeneratorChannels
from utils.emotes import get_emoji


class AddGenerators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "VC"
    
    @commands.hybrid_command(name="setup-vc-generator", description="Set up vc generator channels for this guild", aliases=["setupvcgen", "generator"])
    @commands.guild_only()
    @discord.app_commands.describe(channel="The generator voice channel")
    async def add_generator(self, ctx: commands.Context, channel: discord.VoiceChannel=None):
        if not ctx.author.guild_permissions.manage_channels:
            crossmark = get_emoji("crossmark")
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Manage Channels** permission to you this command."))

        if not channel:
            channel = ctx.channel
        if not isinstance(channel, discord.VoiceChannel):
            blobcatred = get_emoji("blobcatred")
            return await ctx.send(embed=discord.Embed(description=f"{blobcatred} Please provide a **Voice Channel**."))
        channel_id = str(channel.id)
        guild_id = str(ctx.guild.id)
        generate_channel = GeneratorChannels.get_to_save(channel_id, guild_id)
        generate_channel.channel_name = channel.name
        generate_channel.save()
        checkmark = get_emoji("checkmark")
        embed=discord.Embed(description=f"**Target : {channel.mention}**\n{checkmark} This channel is set as a vc generator channel")
        return await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AddGenerators(bot))