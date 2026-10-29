import discord
from discord.ext import commands
from utils.accountage import get_account_age
from banner_maker_wrapper import banner_maker
import io
import base64
import asyncio
from utils import ids

guild_id = ids.my_guild_id
general_channel_id = ids.general_channel_id
farewell_channel_id = ids.farewell_channel_id

class Farewell(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.id != guild_id or member.bot:
            return
        guild = member.guild
        general_channel = guild.get_channel(general_channel_id)
        farewell_channel = guild.get_channel(farewell_channel_id)

        embed1 = discord.Embed(
            description=f"Goodbye, {member.display_name} ({member.name})"
        )
        embed1.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed1.set_footer(text=f"Member count : {guild.member_count}")
        await asyncio.sleep(5)
        await general_channel.send(embed=embed1, delete_after=10)

        embed2 = discord.Embed(title=f"Goodbye {member.display_name}, you will be missed")
        embed2.set_image(url="attachment://banner.jpg")
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        enc_banner_image = await banner_maker(
            avatar,
            f"Farewell, {member.name}!",
            "We will miss you",
            bg="1.png",
        )
        banner_image = discord.File(
            io.BytesIO(base64.b64decode(enc_banner_image)), filename="banner.jpg"
        )
        await farewell_channel.send(embed=embed2, file=banner_image)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Farewell(bot))