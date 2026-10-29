import discord
from discord.ext import commands

def check_vc_permission(permission: str):
    async def predicate(ctx: commands.Context):
        # Admins always pass
        if ctx.author.guild_permissions.administrator:
            return True
        # Ensure user is in a VC
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CheckFailure("You're not connected to a voice channel.")

        channel: discord.VoiceChannel = ctx.author.voice.channel

        perms = channel.permissions_for(ctx.author)

        if not getattr(perms, permission, False):
            raise commands.CheckFailure(f"You need **{permission.replace('_', ' ').title()}** permission in your current voice channel.")
        return True

    return commands.check(predicate)