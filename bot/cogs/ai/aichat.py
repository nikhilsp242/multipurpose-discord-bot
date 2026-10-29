import discord
from discord.ext import commands
import re


class AIChat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot_name = "Kaoru"
    
    async def respond(self, message: discord.Message):
        aicog = self.bot.get_cog("AI")
        if not aicog:
            return await message.reply("Cog not loaded")
        try:
            cleaned_message = self.replace_mentions_with_names(message.content, message)
            context = aicog.get_context(message, cleaned_message)
            headers, payload = aicog.prepare_packets(context)
            await aicog.send_ai_response(message, headers, payload)
        except Exception as e:
            print(e)

    def replace_mentions_with_names(self, content: str, message: discord.Message) -> str:
        if not message.guild:
            return content
        def replace_match(match: re.Match) -> str:
            user_id = int(match.group(1))
            member = message.guild.get_member(user_id)
            if member:
                return member.display_name
            return match.group(0)  

        return re.sub(r"<@!?(?P<id>\d+)>", replace_match, content)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.author == self.bot.user) or message.author.bot:
            return
        ctx = await self.bot.get_context(message)
        if ctx.valid and ctx.command:
            return
        
        if message.reference and isinstance(message.reference.resolved, discord.Message):
            replied_to = message.reference.resolved
            if replied_to.author == self.bot.user and replied_to.embeds:
                return
        if message.guild:
            if self.bot.user in message.mentions or self.bot_name.lower() in message.content.lower():
                async with message.channel.typing():
                    await self.respond(message)
        else:
            async with message.channel.typing():
                await self.respond(message)

    
async def setup(bot: commands.Bot):
    await bot.add_cog(AIChat(bot))