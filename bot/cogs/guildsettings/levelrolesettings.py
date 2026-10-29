import discord
from discord.ext import commands
from models.levelroles import LevelRole
from models.levelup import LevelUpConfig
from utils.assignroles import add_level_role
from utils.emotes import get_emoji

class LevelRoleSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Settings"
    
    @commands.hybrid_command(name="setup-level-roles", description = "Set up level roles for this guild", aliases = ["setlvlrole", "setlevelrole"])
    @commands.guild_only()
    @discord.app_commands.describe(
        role = "The role to be assigned",
        level = "The level for which the role should be assigned",
        xp = "The xp required to earn the role",
        perks = "The perks available for the level")
    async def set_level_roles(self, ctx: commands.Context, role: discord.Role, level: int, xp: int = None, perks: str = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_roles:
                crossmark = get_emoji("crossmark")
                return await ctx.send(
                    embed=discord.Embed(description=f"{crossmark} You need **Manage Roles** permission to use this command.")
                )
            if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                crossmark = get_emoji("crossmark")
                return await ctx.send(
                    embed=discord.Embed(description=f"{crossmark} Please choose role below your top role.")
                )
            bot_member = ctx.guild.me
            if not ctx.guild.me.guild_permissions.manage_roles:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} I need **Manage Roles** permission to assign roles."))
            if role >= bot_member.top_role:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} I can't assign the role {role.mention}. Please hoist my role or choose a role lower than my top role"))
            guild_id = str(ctx.guild.id)
            crossmark = get_emoji("crossmark")
            blobcat = get_emoji("blobcatred")
            guildsetting = LevelUpConfig.get(guild_id)
            if level < 0:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} Please a number greater than 0"))
            if not guildsetting.custom_levelup_system:
                if level > 20:
                    return await ctx.send(embed=discord.Embed(description=f"{blobcat} The default level up system only allows levels upto 20\nIf you want to add more than 20 roles then please enable custom level up system."))
                if xp:
                    return await ctx.send(embed=discord.Embed(description=f"{blobcat} Default level up system uses default xp values. No need to provide xp value."))
            if guildsetting.custom_levelup_system and not xp:
                return await ctx.send(embed=discord.Embed(description=f"{blobcat} Uh oh! I was expecting XP value, because custom level up system is enabled for this guild."))
            required_xp = xp if guildsetting.custom_levelup_system else default_level_up_dict[level]
            level_role = LevelRole.get(guild_id, required_xp)
            # if level_role.role_id == str(role.id):
            #     return await ctx.send(embed=discord.Embed(description=f"{crossmark} This role is already added as **level {level_role.level}**. Please choose another role."))
            # if level_role.level == level:
            #     return await ctx.send(embed=discord.Embed(description=f"{crossmark} A role has already assigned for **level {level}**. Please choose another level."))
            level_role.role_id = str(role.id)
            level_role.level = level
            if guildsetting.custom_levelup_system:
                level_role.xp_required = xp
            else:
                level_role.xp_required = required_xp  
            if perks:
                level_role.level_perks = perks
            level_role.save()
            checkmark = get_emoji("checkmark")
            return await ctx.send(embed=discord.Embed(description=f"{checkmark} {role.mention} added as level **{level}**."))


default_level_up_dict = {
    20: 200000,
    19: 150000,
    18: 100000,
    17: 90000,
    16: 80000,
    15: 70000,
    14: 60000,
    13: 50000,
    12: 40000,
    11: 30000,
    10: 25000,
    9: 20000,
    8: 15000,
    7: 10000,
    6: 7500,
    5: 5000,
    4: 2500,
    3: 500,
    2: 100,
    1: 50
}

async def setup(bot: commands.Bot):
    await bot.add_cog(LevelRoleSettings(bot))