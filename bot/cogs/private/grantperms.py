import discord
from discord.ext import commands
from utils.emotes import get_emoji
from utils import ids

my_guild_id = ids.my_guild_id


class GrantPerms(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"
    
    @commands.command(name="grant", description="Grant permission to members", aliases=["gp", "addp", "grant-perm", "add-perm"])
    @commands.guild_only()
    async def grant(self, ctx: commands.Context, user: discord.Member, *, permission: str):
        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.reply(embed=discord.Embed(description=f"Nice try!\n# {get_emoji('wumpusDance')}"))
        if permission:
            permission = permission.lower()
        if permission not in ROLE_MAP:
            return await ctx.reply(embed=discord.Embed(f"{get_emoji('crossmark')} Invalid permission. Choose from: {', '.join(ROLE_MAP.keys())}"), mention_author = False)
        guild = ctx.guild
        role_name = ROLE_MAP[permission]
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            return await ctx.reply(embed=discord.Embed(description=f"{get_emoji('crossmark')} Role not found for {permission}"), mention_author = False)
        if ctx.author.top_role <= role and ctx.author != ctx.guild.owner:
            return await ctx.reply(embed=discord.Embed(description=f"{get_emoji('blobcatred')} You can only manage roles below your top role"), mention_author = False)
        if ctx.author!= ctx.guild.owner and ctx.author.top_role <= user.top_role:
            return await ctx.reply(embed=discord.Embed(description=f"{get_emoji('blobcatred')} You're not powerful enough to grant permission to {user.mention}"), mention_author=False)
        try:
            await user.add_roles(role)
            checkmark = get_emoji("checkmark")
            embed = discord.Embed(description=f"{checkmark} {user.mention} has been granted **{decode_perm[permission]}** permission." )
            await ctx.reply(embed = embed, mention_author = False)
        except Exception as e:
            await ctx.reply(embed=discord.Embed(description=f"{get_emoji('crossmark')} {e}"))
    
    @commands.command(name="deny", description="Deny permission to members", aliases=["dp", "removep", "deny-perm", "remove-perm", "rp"])
    @commands.guild_only()
    async def deny(self, ctx: commands.Context, user: discord.Member, *, permission: str):
        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.reply(embed=discord.Embed(description=f"Nice try!\n# {get_emoji('wumpusDance')}"))
        if permission:
            permission = permission.lower()
        if permission not in ROLE_MAP:
            return await ctx.reply(embed=discord.Embed(f"{get_emoji('crossmark')} Invalid permission. Choose from: {', '.join(ROLE_MAP.keys())}"), mention_author = False)
        guild = ctx.guild
        role_name = ROLE_MAP[permission]
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            return await ctx.reply(embed=discord.Embed(description=f"{get_emoji('crossmark')} Role not found for {permission}"), mention_author = False)
        if ctx.author.top_role <= role and ctx.author != ctx.guild.owner:
            return await ctx.reply(embed=discord.Embed(description=f"{get_emoji('blobcatred')} You can only manage roles below your top role"), mention_author = False)
        if ctx.author!= ctx.guild.owner and ctx.author.top_role <= user.top_role:
            return await ctx.reply(embed=discord.Embed(description=f"{get_emoji('blobcatred')} You're not powerful enough to deny permission for {user.mention}"), mention_author=False)
        try:
            await user.remove_roles(role)
            checkmark = get_emoji("checkmark")
            embed = discord.Embed(description=f"{checkmark} **{decode_perm[permission]}** permission has been removed from {user.mention}" )
            await ctx.reply(embed = embed, mention_author = False)
        except Exception as e:
            await ctx.reply(embed=discord.Embed(description=f"{get_emoji('crossmark')} {e}"))
    
    @commands.command(name="permguide", description="Guide for mods to use `grant` command", aliases=["pg", "perms"])
    async def permguide(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Permission Guide",
            description="These are the available permissions for the `grant` command"
        )

        for perm_key, perm_desc in decode_perm.items():
            embed.add_field(name=f'`{perm_key}`', value=perm_desc, inline=False)

        await ctx.reply(embed=embed, mention_author=False)
            

ROLE_MAP = {
    "kick": "kp", 
    "ban": "bp",  
    "mod": "tp",  
    "admin": "ap",
    "channel": "cp", 
    "role": "rp",
    "all" : "aEap",
    "message": "mp", 
    "nick": "np",
    "vc": "vp",
    "ping" : "pp"
    
}

decode_perm = {
    "kick": "Kick Members",
    "ban": "Ban Members",
    "mod": "Moderate / Timeout Members",
    "admin": "Administrator",
    "channel": "Manage Channels",
    "role": "Manage Role",
    "all": "All (expect Administrator)",
    "message": "Manage Messages",
    "nick": "Manage Nicknames",
    "vc": "Manage Voicechannels",
    "ping": "Mention roles, @everyone and @here"
}        


async def setup(bot: commands.Bot):
    await bot.add_cog(GrantPerms(bot))