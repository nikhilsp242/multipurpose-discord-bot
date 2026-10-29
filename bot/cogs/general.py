from discord.ext import commands
from database.setup import setup_tables

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="png")
    async def ping(self, ctx):
        """Ping the bot."""
        await ctx.send("Pong!")

    # @commands.command()
    # async def resetdb(self, ctx):
    #     import os
    #     os.remove("data/botdata.db")
    #     setup_tables()
    #     await ctx.send("Database has been reset.")

    
async def setup(bot):
    await bot.add_cog(General(bot))


# import aiohttp
# import os

# # Bot setup
# intents = discord.Intents.default()
# bot = commands.Bot(command_prefix='!', intents=intents)

# # Your Tenor API key
# TENOR_API_KEY = 'your_tenor_api_key_here'

# @bot.command()
# async def action(ctx, *, search_term: str):
#     """Fetches a GIF from Tenor based on a search term (e.g., hug, slap)."""
#     async with aiohttp.ClientSession() as session:
#         params = {
#             "q": search_term,
#             "key": TENOR_API_KEY,
#             "limit": 1,
#             "media_filter": "minimal"
#         }
#         async with session.get("https://tenor.googleapis.com/v2/search", params=params) as r:
#             if r.status != 200:
#                 await ctx.send("Couldn't fetch GIF 😢")
#                 return
#             data = await r.json()
#             if data.get("results"):
#                 gif_url = data["results"][0]["media_formats"]["gif"]["url"]
#                 await ctx.send(f"{ctx.author.display_name} does **{search_term}**!\n{gif_url}")
#             else:
#                 await ctx.send("No GIFs found.")

# # Run your bot
# bot.run("your_discord_token")

    