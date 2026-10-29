import discord
from discord.ext import commands
import typing
from utils.emotes import get_emoji
from utils import ids

my_guild_id = ids.my_guild_id

class Rename(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"
    
    @commands.hybrid_command(name="nick", description="Set or reset nick name of an user")
    @commands.guild_only()
    @discord.app_commands.describe(
        user="Select user to set or reset their nick name",
        nickname="The name to set (leave blank to reset)"
    )
    async def nick(self, ctx: commands.Context, user: discord.Member=None, * , nickname=None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_nicknames:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("crossmark")} You need **Manage Nickname** permission to use this command."))
            if ctx.guild.id != my_guild_id:
                if user != ctx.author and user.top_role>=ctx.author.top_role:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{get_emoji("blobcatred")} You can only manage nicknames of members below your top role."))
            if not user:
                user = ctx.author
            if user == ctx.guild.owner:
                return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{get_emoji("blobcatfear")} This user is way too powerful to change their nick name."))
            if user.top_role >= ctx.guild.me.top_role:
                return await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{get_emoji("nyaSob")} This user is not below my top role."))
            try:
                old_name = user.display_name
                await user.edit(nick=nickname)
                new_name = f"**{nickname}**" if nickname else "**Default Nickname**"
                await ctx.send(embed=discord.Embed(description=f"**Target : {user.mention}**\n{get_emoji("checkmark")} Nickname changed from **{old_name}** to {new_name}"))
            except discord.Forbidden:
                await ctx.send(embed=discord.Embed(description=f"{get_emoji("nyaSob")} I don't have permission to change nicknames."))
            except discord.HTTPException as e:
                await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} An error occurred: {e}"))
    
    @commands.command(name="rename", description="Rename any target object or user")
    @commands.guild_only()
    async def rename(self, ctx: commands.Context, target: typing.Union[discord.Emoji, discord.abc.GuildChannel, discord.Member, discord.Role],* , name):
        async with ctx.typing():
            old_name = None
            is_emoji = False
            is_user = False
            if isinstance(target, discord.Emoji):
                if not ctx.author.guild_permissions.manage_emojis_and_stickers:
                    return await ctx.send(embed=discord.Embed(description=f"**Target Emoji**\n# {target}\n{get_emoji("crossmark")} You need **Manage Emojis and Stickers** permission to rename this target."))
                old_name = target.name
                is_emoji = True
            elif isinstance(target, discord.abc.GuildChannel):
                if not ctx.author.guild_permissions.manage_channels:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {target.mention}**\n{get_emoji("crossmark")} You need **Manage Channels** permission to rename this target."))
                old_name = target.name
            elif isinstance(target, discord.Role):
                if not ctx.author.guild_permissions.manage_roles:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {target.mention}**\n{get_emoji("crossmark")} You need **Manage Roles** permission to rename this target."))
                if ctx.author != ctx.guild.owner and ctx.author.top_role <= target:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {target.mention}**\n{get_emoji("blobcatred")} You can only edit roles below your top role."))
                old_name = target.name
            elif isinstance(target, discord.Member):
                if not ctx.author.guild_permissions.manage_nicknames:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {target.mention}**\n{get_emoji("crossmark")} You need **Manage Nicknames** permission to rename this target."))
                if target == ctx.guild.owner:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {target.mention}**\n{get_emoji("blobcatred")} Cannot change owner's nickname."))
                if ctx.author.top_role <= target.top_role:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {target.mention}**\n{get_emoji("blobcatred")} You can only change nicknames of members below your top role."))
                old_name = target.display_name
                is_user = True
            else:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} No valid target detected for renaming."), delete_after=5)
            try:
                if is_user:
                    await target.edit(nick=name)
                else:
                    await target.edit(name=name)
                target_format = f"**Target Emoji**\n# {target}" if is_emoji else f"**Target : {target.mention}**"
                embed = discord.Embed(description=f"{target_format}\n{get_emoji("checkmark")} Target renamed from **{old_name}** to **{name}**")
                await ctx.send(embed=embed)
            except discord.Forbidden as e:
                await ctx.send(embed=discord.Embed(description=f"{get_emoji("nyaSob")} I don't have permission to rename the target: {e}"))
            except discord.HTTPException as e:
                await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} An error occurred: {e}"))


    
async def setup(bot: commands.Bot):
    await bot.add_cog(Rename(bot))      