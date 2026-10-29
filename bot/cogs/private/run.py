import discord
from discord.ext import commands
import io
import contextlib
import textwrap
from utils import bot_instance

bot = bot_instance.instance

class Execute(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"
    
    @commands.command(name="run", description="Run python scripts", aliases=["execute","exe"])
    async def run(self, ctx: commands.Context, *, code: str):
        if ctx.author.id not in {1194815627324571668, 797359552874020954}: return 
        async with ctx.typing():
            str_io = io.StringIO()
        with contextlib.redirect_stdout(str_io):
            try:
                if code.startswith("```") and code.endswith("```"):
                    code = code.strip("```")
                    if code.startswith("python"):
                        code = code[len("python"):].strip()
                    elif code.startswith("py"):
                        code = code[len("py"):].strip()
    
                else:
                    code = code.strip()

                exec(f"async def _exec_code(ctx):\n{textwrap.indent(code, '    ')}")


                await locals()["_exec_code"](ctx)

            except Exception as e:
                await ctx.send(f"Error during execution: {e}")


        output = str_io.getvalue()
        try:
            if output:
                await ctx.send(f"Output: ```{output}```")
            else:
                await ctx.send("Code executed successfully")
        except discord.errors.NotFound as e:
            if output:
                await ctx.author.send(f"Output: ```{output}```")
            else:
                await ctx.author.send("Code executed successfully")
            await ctx.author.send(f"Sending direct message because of an exception of an error : {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Execute(bot))