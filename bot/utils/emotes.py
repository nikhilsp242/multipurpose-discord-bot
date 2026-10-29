import discord
from utils import bot_instance


bot = bot_instance.instance

def get_emoji(name):
    for guild in bot.guilds:
        emoji = discord.utils.get(guild.emojis, name=name)
        if emoji:
            return emoji
    return None