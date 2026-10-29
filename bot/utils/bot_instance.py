import discord
from discord.ext import commands
import config

command_prefix = config.PREFIXS
intents = discord.Intents.all()  
status = discord.Status.offline

instance = commands.Bot(command_prefix=command_prefix, case_insensitive=True , intents=intents, status=status)
instance.remove_command("help")
