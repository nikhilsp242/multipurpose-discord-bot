import discord
from discord.ext import commands
from utils.emotes import get_emoji

my_guild_id = 1183064183646982164
qrt_id = 1287861917917904898
quarantine_role_id = 1287855137255198750

class Quarantine(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"
    
    @commands.command(name="quarantine", description="Quarantine an user", aliases=["qrt"])
    @commands.guild_only()
    async def quarantine(self, ctx: commands.Context, user: discord.Member, *, reason=None):
        if ctx.guild.id != my_guild_id:
            return
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Administrator** permission to use this command."))
        if user.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n.{get_emoji('crossmark')} Cannot quarantine admins."))
        if ctx.author != ctx.guild.owner and ctx.author.top_role <= user.top_role:
            return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n.{get_emoji('crossmark')} You can only quarantine members below your top role."))
        mute_role = discord.utils.get(ctx.guild.roles, id=quarantine_role_id)
        if not mute_role:
            await ctx.send("Quarantine role not found.")
            return
        await user.add_roles(mute_role)
        checkmark = get_emoji("checkmark")
        embed = discord.Embed(description=f"{user.mention} ({user.name}) has been quarantined. {checkmark}")
        embed.add_field(name="Reason", value=reason if reason else "Not specified")
        await ctx.reply(embed=embed, mention_author = False)
    
    @commands.command(name="release", description="Quarantine an user", aliases=["remove-quarantine", "remove-qrt"])
    @commands.guild_only()
    async def release(self, ctx: commands.Context, user: discord.Member):
        if ctx.guild.id != my_guild_id:
            return
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Administrator** permission to use this command."))
        if user.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n.{get_emoji('crossmark')} Cannot release admins."))
        if ctx.author != ctx.guild.owner and ctx.author.top_role <= user.top_role:
            return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n.{get_emoji('crossmark')} You can only release members below your top role."))
        mute_role = discord.utils.get(ctx.guild.roles, id=quarantine_role_id)
        if not mute_role:
            await ctx.send("Quarantine role not found.")
            return
        await user.remove_roles(mute_role)
        checkmark = get_emoji("checkmark")
        embed = discord.Embed(description=f"{user.mention} ({user.name}) has been released. {checkmark}")
        await ctx.reply(embed=embed, mention_author = False)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Quarantine(bot))