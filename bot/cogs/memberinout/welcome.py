import discord
from discord.ext import commands
from utils.accountage import get_account_age
from banner_maker_wrapper import banner_maker
import io
import base64
from utils import ids

guild_id = ids.my_guild_id
welcome_channel_id = ids.welcome_channel_id
general_channel_id = ids.general_channel_id
welcome_role_id = ids.welcome_role_id
member_role_id = ids.member_role_id
bot_role_id = ids.bot_role_id

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != guild_id:
            return
        guild = member.guild
        if member.bot:
            bot_role = guild.get_role(bot_role_id)
            await member.add_roles(bot_role)
            return
        member_role = guild.get_role(member_role_id)
        await member.add_roles(member_role)

        embed1 = discord.Embed(
            title = f"Welcome to {guild.name}, {member.display_name}!",
            description=f"We're glad to have you here, {member.mention}!"
        )
        embed1.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed1.add_field(name="Account Age", value=get_account_age(member))
        embed1.set_footer(text=f"Member count : {guild.member_count}")

        general_channel = guild.get_channel(general_channel_id)
        welcome_role = guild.get_role(welcome_role_id)

        await general_channel.send(welcome_role.mention, embed=embed1)


        embed2 = discord.Embed(
            title=f"Welcome to {guild.name}, {member.display_name}!",
            color=0x000000, 
        )
        embed2.set_image(url="attachment://banner.jpg")
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        enc_banner_image = await banner_maker(
            avatar,
            f"Welcome, {member.name}!",
            "Hope you enjoy your stay!",
            bg="1.png",
        )
        banner_image = discord.File(
            io.BytesIO(base64.b64decode(enc_banner_image)), filename="banner.jpg"
        )
        welcome_channel = guild.get_channel(welcome_channel_id)
        await welcome_channel.send(embed=embed2, file=banner_image)
    

# async def setup(bot: commands.Bot):
#     await bot.add_cog(Welcome(bot))