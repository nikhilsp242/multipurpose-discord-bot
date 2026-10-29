import re
from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
from utils import ids

guild_id = ids.my_guild_id
log_channel_id = ids.log_channel_id 

invite_regex = re.compile(
    r"(?:https?://)?(?:www\.)?(?:discord(?:\.gg|(?:app)?\.com/invite))/([a-zA-Z0-9\-]+)",
    re.IGNORECASE
)

class AntiInviteSpam(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.timeout_duration = timedelta(minutes=10)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return

        await self.on_message(after)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.guild.id != guild_id:
            return

        if (
            message.author == message.guild.me
            or message.author.guild_permissions.administrator
        ):
            return


        matches = invite_regex.findall(message.content)
        if not matches:
            return

        for code in matches:
            try:
                invite = await self.bot.fetch_invite(code, with_counts=False)
                if invite.guild and invite.guild.id == guild_id:
                    # It's an invite to this server; ignore
                    continue

                await message.delete()
                await self.timeout_member(
                    member=message.author,
                    guild=message.guild,
                    reason="Sent invite link to another server.",
                    channel=message.channel
                )
                break  # Act on first external invite found
            except discord.NotFound:
                # Invalid invite, ignore
                continue
            except Exception as e:
                print(f"[AntiInviteSpam Error]: {e}")

    async def timeout_member(self, member, guild, reason, channel):
        until = datetime.now(timezone.utc) + self.timeout_duration
        try:
            await member.timeout(until, reason=reason)
            embed = discord.Embed(
                title="Invite Link Detected",
                description=f"{member.mention} has been timed out.\nReason: {reason}",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            log_channel = guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            await channel.send(embed=embed)
        except Exception as e:
            print(f"[AntiInviteSpam Error]: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiInviteSpam(bot))
