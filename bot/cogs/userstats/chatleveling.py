import discord
from discord.ext import commands
from models.userstats import UserStats
from models.channels import Channel
from models.levelup import LevelUpConfig
from models.messagecount import MessageCount
from utils.assignroles import add_level_role
from config import coinsPerMessage , xpPerMessage

class ChatLeveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot and not message.author.id == self.bot.user.id:
            return
        if not message.guild:
            return
        isMainChannel = False
        user_id = str(message.author.id)
        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)
        guild = message.guild
        member = guild.get_member(message.author.id)
        data = UserStats.get_one(user_id, guild_id)
        data.total_messages += 1
        
        if message.reference:
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                if replied_message.author != message.author:
                    id = str(replied_message.author.id)
                    data.update_field(id, guild_id, "replies_received", 1)
            except Exception as e:
                pass

        if message.attachments:
            data.total_attachments += len(message.attachments)

        guildsettings = LevelUpConfig.get(guild_id)
        channel = Channel.get(channel_id, guild_id)         
        if channel.is_main_channel:
            data.main_channel_messages += 1
            isMainChannel = True
        if channel.is_coin_channel or guildsettings.enable_coins_for_all_channels:
            data.balance += coinsPerMessage * (guildsettings.booster_coin_multiplier if member.premium_since else 1)
        if channel.is_xp_channel or guildsettings.enable_xp_for_all_channels:
            data.xp += xpPerMessage * (guildsettings.booster_xp_multiplier if member.premium_since else 1)


        if not guildsettings.levelup_enabled:
            data.save()
            countMessages(user_id, guild_id, isMainChannel)
            return
        levelup_channel_id = guildsettings.levelup_channel
        levelup_channel = guild.get_channel(int(levelup_channel_id))
        level = await add_level_role(member, data.xp, data.level, levelup_channel)
        if level > data.level:
            data.level = level
        data.save()
        countMessages(user_id, guild_id, isMainChannel)



def countMessages(user_id, guild_id, isMainChannel):
    messages = MessageCount.get_one(user_id, guild_id)
    if not messages:
        messages = MessageCount(user_id=user_id, guild_id=guild_id)
    messages.daily_messages += 1
    messages.weekly_messages += 1
    messages.monthly_messages += 1
    if isMainChannel:
        messages.daily_main_channel_messages += 1
        messages.weekly_main_channel_messages += 1
        messages.monthly_main_channel_messages += 1
    messages.save()


async def setup(bot):
    await bot.add_cog(ChatLeveling(bot))