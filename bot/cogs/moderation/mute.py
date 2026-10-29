import discord
from discord.ext import commands
from utils.emotes import get_emoji

class Mute(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"
    
    @commands.command(name="mute", description="Mute an user in the current channel")
    @commands.guild_only()
    async def mute(self, ctx: commands.Context, user: discord.Member, *, reason=None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.moderate_members:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Moderate Members** permission to use this command."))
            if user.guild_permissions.administrator:
                return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{get_emoji('blobcatred')} Cannot mute administrators."))
            if ctx.author != ctx.guild.owner and ctx.author.top_role <= user.top_role:
                return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{get_emoji('blobcatred')} You can only mute members below your top role."))
            channel = ctx.channel
            role_name = f"{channel.name}-mute"
            try:
                mute_role = discord.utils.get(ctx.guild.roles, name=role_name)
                if not mute_role:

                    mute_role = await ctx.guild.create_role(name=role_name, reason=f"Temp mute for {channel.name}")
                    overwrite = discord.PermissionOverwrite()
                    overwrite.send_messages = False
                    await channel.set_permissions(mute_role, overwrite=overwrite)

                await user.add_roles(mute_role)
                checkmark = get_emoji("checkmark")
                embed = discord.Embed(description=f"{checkmark} {user.mention} has been muted in {channel.mention}.")
                embed.add_field(name="Reason", value=f"{reason if reason else "Not provided"}")
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"Failed to mute : {e}"))
    
    @commands.command(name="unmute", description="Unmute an user in the current channel")
    @commands.guild_only()
    async def unmute(self, ctx: commands.Context, user: discord.Member):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.moderate_members:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Moderate Members** permission to use this command."))
            if user.guild_permissions.administrator:
                return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{get_emoji('blobcatred')} Cannot unmute administrators."))
            if ctx.author != ctx.guild.owner and ctx.author.top_role <= user.top_role:
                return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{get_emoji('blobcatred')} You can only unmute members below your top role."))
            channel = ctx.channel
            role_name = f"{channel.name}-mute"
            try:
                mute_role = discord.utils.get(ctx.guild.roles, name=role_name)
                if mute_role:

                    await user.remove_roles(mute_role)
                    await mute_role.delete(reason=f"Unmuted user in {channel.name}")
                    checkmark = get_emoji("checkmark")
                    embed = discord.Embed(description=f"{checkmark} {user.mention} has been unmuted in {channel.mention}.")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"No one is muted in this channel : {channel.mention}.")
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"Failed to unmute : {e}"))
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Mute(bot))