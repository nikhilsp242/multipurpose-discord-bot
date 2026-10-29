import discord
from models.levelroles import LevelRole
from utils import bot_instance
from utils.emotes import get_emoji

bot = bot_instance.instance

# async def add_level_role(member: discord.Member, xp: int, current_level: int , channel: discord.TextChannel=None):
#     guild_id = str(member.guild.id)
    
#     level_role = LevelRole.get(guild_id, xp)
#     print(level_role.__dict__)
#     if not level_role.role_id:
#         return 0
#     if level_role:
#         current_level = level_role.level
#         role = member.guild.get_role(int(level_role.role_id))
#         if role:
#             try:
#                 await member.add_roles(role, reason="Level Up")
#                 if member.bot:
#                     return current_level
#                 if channel:
#                     lvlup = get_emoji("lvlup")
#                     confetti = get_emoji("confetti")
#                     perks = ""
#                     if level_role.level_perks:
#                         perks = f"{confetti} **You earned :** {level_role.level_perks}"
#                     embed = discord.Embed(
#                         title="Level Up",
#                         description=f"{lvlup} GG! You reached **level {current_level}**\n{perks}"
#                         )
#                     embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
#                     await channel.send(member.mention, embed=embed)
#                 return current_level
#             except Exception as e:
#                 await member.guild.owner.send(f"An error occurred during the level up process : {e}")
#                 return 0
#     return current_level
                


async def add_level_role(member: discord.Member, xp: int, current_level: int , channel: discord.TextChannel=None):
    guild_id = str(member.guild.id)
    
    level_role = LevelRole.get(guild_id, xp)
    if not level_role.role_id:
        return 0
    if level_role and level_role.level > current_level:
        current_level = level_role.level
        role = member.guild.get_role(int(level_role.role_id))
        if role and role not in member.roles:
            try:
                await member.add_roles(role, reason="Level Up")
                if member.bot:
                    return current_level
                if channel:
                    lvlup = get_emoji("lvlup")
                    confetti = get_emoji("confetti")
                    perks = ""
                    if level_role.level_perks:
                        perks = f"{confetti} **You earned :** {level_role.level_perks}"
                    embed = discord.Embed(
                        title="Level Up",
                        description=f"{lvlup} GG! You reached **level {current_level}**\n{perks}"
                        )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                    await channel.send(member.mention, embed=embed)
                return current_level
            except Exception as e:
                await member.guild.owner.send(f"An error occurred during the level up process : {e}")
                return 0
    return current_level    