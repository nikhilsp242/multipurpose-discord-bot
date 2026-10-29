import discord
from discord.ext import commands
from typing import Tuple, Dict, List
from collections import defaultdict, deque
from models.aidata import AIData
import aiohttp
import json
import asyncio
from utils.emotes import get_emoji
import re


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot_name = "Kaoru"
        self.api_key = "bbc3ce417adf52dd0d3c0677f361e48a53eeb068af15991fd9efc3461b093e8b"
        self.conversation_memory = defaultdict(lambda: deque(maxlen=4))
        for command in self.get_commands():
            command.cog_category = "AI"
    
    @commands.hybrid_command(name="clear-memory", description="Clears conversation memory for a particular user and a particular channel")
    @discord.app_commands.describe(
        user="Select user to clear their conversation memory",
        channel="Select channel to clear it's conversation memory"
    )
    async def clear_memory(self, ctx: commands.Context, user: discord.Member = None, channel: discord.abc.GuildChannel = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            user = user if user else ctx.author
            channel = channel if channel else ctx.channel
            if isinstance(channel, discord.abc.GuildChannel):
                if not ctx.author.guild_permissions.administrator:
                    return await ctx.send(embed=discord.Embed(description=f"{get_emoji('crossmark')} You need **Administrator** permission to use this command."))
            elif isinstance(channel, discord.DMChannel):
                user = None
            if user:
                keys_to_delete = [(channel.id, user.id)]
            else:
                keys_to_delete = [
                    key for key in self.conversation_memory.keys()
                    if key[0] == channel.id
                ]
            for key in keys_to_delete:
                if key in self.conversation_memory:
                    del self.conversation_memory[key]
            user_id = str(user.id) if user else None
            AIData.delete(str(channel.id), user_id)
            await ctx.send(embed=discord.Embed(description=f"{get_emoji('checkmark')} Successfully cleared conversation memory."))

    def get_context(self, message: discord.Message, user_prompt: str) -> List[Dict[str, str]]:
        key = (message.channel.id, message.author.id)

        if key not in self.conversation_memory:
            data_list = AIData.get(str(message.channel.id), str(message.author.id))
            dq = deque(maxlen=4)
            for data in data_list:
                dq.append({"role": data.role, "content": data.content})
            self.conversation_memory[key] = dq

        channel_memory = list(self.conversation_memory[key])
        context = []

        if message.reference and message.reference.resolved:
            referenced_message = message.reference.resolved
            referenced_content = referenced_message.content

            in_memory = any(
                referenced_content.strip() == m["content"].strip()
                for m in channel_memory
            )
            if not in_memory:
                context.append({"role": "user", "content": f"(referencing) {referenced_content}"})

        context.extend(channel_memory)

        context.append({"role": "user", "content": user_prompt})

        return context


    def update_memory(self, channel_id: int, user_id: int, role: str, content: str):
        key = (channel_id, user_id)
        self.conversation_memory[key].append({"role": role, "content": content})

        AIData(
            channel_id=str(channel_id),
            user_id=str(user_id),
            role=role,
            content=content
        ).save()
    
    def prepare_packets(self, context: List[Dict[str, str]]) -> Tuple[Dict, Dict]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a cute and smart assistant called {self.bot_name}. Keep you responses very short and concise. You talk like a real person and you're lazy to type, so you keep your responses short. Avoid introducing yourself unless asked. Do not ask any questions. Do not refer to yourself in the third person."
                },
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "hello ^^"},
                {"role": "user", "content": "wassup"},
                {"role": "assistant", "content": "all good, wbu?"},
                {"role": "user", "content": "i love you"},
                {"role": "assistant", "content": "hehe, thank you :3"}
            ] + context,
            "temperature": 0.5
        }
        return headers, payload
    
    def remove_html_if_present(self, text: str) -> str:
        if re.search(r"<[^>]+>", text):
            text = re.sub(r"<[^>]+>", "", text).strip()
        return text
    
    async def send_ai_response(self, message: discord.Message, headers: Dict, payload: Dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.together.xyz/v1/chat/completions",
                headers=headers,
                json=payload
            ) as resp:
                text = await resp.text()
                if resp.status != 200:
                    response = f"API Error: {resp.status}\n{text[:1000]}"
                    print(response)
                    error_data = await resp.json()
                    print("API error details:", error_data)
                    return await message.reply(get_emoji('wumpusDance'))
                
                try:
                    data = json.loads(text)
                    ai_reply = data["choices"][0]["message"]["content"].strip()
                    if ai_reply.startswith(f"{self.bot_name}:"):
                        ai_reply = ai_reply[len(f"{self.bot_name}:"):].strip()
                except Exception as e:
                    error_msg = f"Error parsing response: {e}\nRaw response: {text[:1000]}"
                    return await message.reply(error_msg)
                
        ai_reply = self.remove_html_if_present(ai_reply)

        
        self.update_memory(message.channel.id, message.author.id, "user", message.content)


        self.update_memory(message.channel.id, message.author.id, "assistant", ai_reply)

        await message.reply(ai_reply[:2000])
    
    async def cleanup_old_memory(self):
        while True:
            AIData.delete_old(minutes=30)  
            await asyncio.sleep(900)
    
    async def cog_load(self):
        self.cleanup_task = asyncio.create_task(self.cleanup_old_memory())

    async def cog_unload(self):
        if hasattr(self, "cleanup_task"):
            self.cleanup_task.cancel()
        await super().cog_unload()

async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
    