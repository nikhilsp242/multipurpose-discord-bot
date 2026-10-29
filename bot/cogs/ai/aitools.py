# import discord
# from discord.ext import commands

# class AITools(commands.Cog):
#     def __init__(self, bot: commands.Bot):
#         self.bot = bot
#         for command in self.get_commands():
#             command.cog_category = "AI"
    
#     async def respond(self, ctx: commands.Context, query):
#         aicog = self.bot.get_cog("AI")
#         if not aicog:
#             return await ctx.reply("Cog not loaded")
#         try:
#             model = aicog.get_model("code")
#             context = aicog.get_context(ctx.message, query)
#             headers, payload = aicog.prepare_packets(model, context)
#             await aicog.send_ai_response(ctx, None, headers, payload)
#         except Exception as e:
#             print(e)

#     @commands.hybrid_command(name="code", description="Get coding related help from AI")
#     @discord.app_commands.describe(query="Your code-related query")
#     async def code_help(self, ctx: commands.Context,* , query: str):
#         if ctx.interaction: await ctx.defer()
#         async with ctx.typing():
#             await self.respond(ctx, query)

# async def setup(bot: commands.Bot):
#     await bot.add_cog(AITools(bot))