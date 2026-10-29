import discord
from discord.ext import commands
import os
import config
import asyncio
from database.setup import setup_tables
from database.update import add_columns , delete_table , delete_row, create_table
from utils import bot_instance

bot = bot_instance.instance


import os 

async def load_cogs():
    # await bot.load_extension("cogs.safetysetup.antispam")
    for root, _, files in os.walk("cogs"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                # Convert path to dotted import (e.g., cogs.leveling.commands)
                path = os.path.join(root, file).replace(os.sep, ".")
                module = path[:-3]  # remove '.py'
                try:
                    await bot.load_extension(module)
                    print(f"✅ Loaded extension: {module}")
                except Exception as e:
                    print(f"❌ Failed to load {module}: {e}")



async def main():
    # setup_tables()
    # create_table()
    # add_columns() 
    # delete_table()
    # delete_row()
    await load_cogs()
    await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())