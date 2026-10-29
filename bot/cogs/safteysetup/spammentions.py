import discord
from discord.ext import commands
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from utils import ids

guild_id = 1175730830371455016
bypass_role_id = ids.spam_bypass_role_id
log_channel_id = ids.log_channel_id

class AntiMentionSpam(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Track per-user deque: deque[(timestamp, mention_count)]
        self.user_mention_history = defaultdict(lambda: deque())

        # Configurable mention thresholds
        self.thresholds = [
            (5, timedelta(seconds=30)),    # 5 mentions in 10 seconds
            (10, timedelta(seconds=60)),   # 10 mentions in 60 seconds
        ]

        self.timeout_duration = timedelta(minutes=10)
        self.max_timeframe = max(tf for _, tf in self.thresholds)

    def is_spamming_mentions(self, user_deque: deque, now: datetime):
        """Check if user exceeded mention thresholds."""
        for threshold, timeframe in self.thresholds:
            total_mentions = sum(count for t, count in user_deque if now - t <= timeframe)
            if total_mentions >= threshold:
                return f"{total_mentions} mentions in {timeframe.seconds} seconds"
        return None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            message.guild is None or
            message.guild.id != guild_id or
            message.author == message.guild.me or
            message.author.guild_permissions.administrator
        ):
            return

        bypass_role = message.guild.get_role(bypass_role_id)
        if bypass_role and bypass_role in message.author.roles:
            return

        # Ignore mentions caused by replying to a message
        mentions = []
        if message.reference and isinstance(message.reference.resolved, discord.Message):
            replied_user_id = message.reference.resolved.author.id
        else:
            replied_user_id = None

        for user in message.mentions:
            if (
                user.id == message.author.id       # ignore self-mention
                or user.bot                        # ignore bot mentions
                or user.id == replied_user_id      # ignore implicit reply mention
            ):
                continue
            mentions.append(user)

        mention_count = len(mentions) + len(message.role_mentions)
        if mention_count == 0:
            return

        now = datetime.now(timezone.utc)
        user_id = message.author.id

        user_deque = self.user_mention_history[user_id]
        user_deque.append((now, mention_count))

        # Efficient cleanup of stale entries
        while user_deque and now - user_deque[0][0] > self.max_timeframe:
            user_deque.popleft()

        # Check mention spam
        reason = self.is_spamming_mentions(user_deque, now)
        if reason and not message.author.is_timed_out():
            await self.timeout_member(
                member=message.author,
                guild=message.guild,
                reason=f"Spam Mentions: {reason}",
                channel=message.channel
            )
            user_deque.clear()

    async def timeout_member(self, member: discord.Member, guild: discord.Guild, reason: str, channel: discord.TextChannel):
        until = datetime.now(timezone.utc) + self.timeout_duration
        try:
            await member.timeout(until, reason=reason)
            embed = discord.Embed(
                title="Anti Mention Spam",
                description=f"{member.mention} has been timed out for spam mentioning.\n**{reason}**",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            log_channel = guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            await channel.send(embed=embed)

        except Exception as e:
            print(f"[AntiMentionSpam Error]: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiMentionSpam(bot))
