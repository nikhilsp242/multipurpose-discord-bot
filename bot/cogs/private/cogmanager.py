import discord
import os
from discord.ext import commands
from utils.emotes import get_emoji

class CogManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"

    @commands.command(name="load")
    async def load_cog(self, ctx: commands.Context, *, cog: str):
        """Loads a cog while the bot is running."""
        if ctx.author.id not in {1194815627324571668, 797359552874020954}: return 
        try:
            await self.bot.load_extension(cog)
            response = f"{get_emoji('checkmark')} Successfully loaded `{cog}`"
        except commands.ExtensionAlreadyLoaded:
            response = f"{get_emoji('warn')} `{cog}` is already loaded."
        except commands.ExtensionNotFound:
            response = f"{get_emoji('crossmark')} Cog `{cog}` not found."
        except Exception as e:
            response = f"{get_emoji('crossmark')} Error loading `{cog}`: `{e}`"
        finally:
            await ctx.send(embed=discord.Embed(description=response))

    @commands.command(name="unload")
    async def unload_cog(self, ctx: commands.Context, *, cog: str):
        """Unloads a cog while the bot is running."""
        if ctx.author.id not in {1194815627324571668, 797359552874020954}: return 
        try:
            await self.bot.unload_extension(cog)
            response = f"{get_emoji('checkmark')} Successfully unloaded `{cog}`"
        except commands.ExtensionNotLoaded:
            response = f"{get_emoji('warn')} `{cog}` is not loaded."
        except commands.ExtensionNotFound:
            response = f"{get_emoji('crossmark')} Cog `{cog}` not found."
        except Exception as e:
            response = f"{get_emoji('crossmark')} Error unloading `{cog}`: `{e}`"
        finally:
            await ctx.send(embed=discord.Embed(description=response))

    @commands.command(name="reload")
    async def reload_cog(self, ctx: commands.Context, *, cog: str):
        """Reloads a cog while the bot is running."""
        if ctx.author.id not in {1194815627324571668, 797359552874020954}: return 
        try:
            await self.bot.reload_extension(cog)
            response = f"{get_emoji('checkmark')} Successfully reloaded `{cog}`"
        except commands.ExtensionNotLoaded:
            response = f"{get_emoji('warn')} `{cog}` is not loaded."
        except commands.ExtensionNotFound:
            response = f"{get_emoji('crossmark')} Cog `{cog}` not found."
        except Exception as e:
            response = f"{get_emoji('crossmark')} Error reloading `{cog}`: `{e}`"
        finally:
            await ctx.send(embed=discord.Embed(description=response))
    
    @commands.command(name="listcogs", aliases=["cogs"])
    async def list_cogs(self, ctx: commands.Context):
        """Lists all currently loaded cogs as a plain message."""
        if ctx.author.id not in {1194815627324571668, 797359552874020954}: return 
        loaded = list(self.bot.extensions.keys())

        # Optional: Scan for available cogs
        all_cogs = []
        for root, _, files in os.walk("cogs"):
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    path = os.path.join(root, file).replace("\\", "/")
                    path = path[:-3] 
                    all_cogs.append(path.replace("/", "."))

        unloaded = [c for c in all_cogs if c not in loaded]

        message_lines = []
        
        if loaded:
            message_lines.append("\n✅ Loaded Cogs:")
            for cog in sorted(loaded):
                message_lines.append(f"✔ {cog}")
        else:
            message_lines.append("\n✅ Loaded Cogs: None")

        if unloaded:
            message_lines.append("\n❌ Unloaded Cogs:")
            for cog in sorted(unloaded):
                message_lines.append(f"✖ {cog}")
        else:
            message_lines.append("\n❌ Unloaded Cogs: None")

        final_message = "\n".join(message_lines)

        if len(final_message) > 4080:
            final_message = final_message[:4080] + "\n... (truncated)"

        await ctx.send(embed=discord.Embed(title="⏻ Cog Status",description=(f"```{final_message}```")))

async def setup(bot: commands.Bot):
    await bot.add_cog(CogManager(bot))
