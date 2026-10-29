import discord
from discord.ext import commands, tasks
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from utils import ids

guild_id = 1175730830371455016
bypass_role_id = ids.spam_bypass_role_id
allowed_channels = {1287754253984858216, 1364972658197921912, 1213088181235224637, 1186635450018967563, 1231142101622984725, 1290329420837552159}
log_channel_id = ids.log_channel_id

class AntiSpam(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Track per-user deque: deque[(timestamp, content_hash)]
        self.user_message_history = defaultdict(lambda: deque())

        # Define thresholds
        self.thresholds = [
            (5, timedelta(seconds=5)),
            (10, timedelta(seconds=30)),
            (30, timedelta(seconds=100))
        ]
        self.repeat_threshold = 3
        self.repeat_timeframe = timedelta(seconds=30)
        self.timeout_duration = timedelta(minutes=10)

    def is_spamming(self, user_deque: deque, now: datetime):
        # Check rate limits
        for threshold, timeframe in self.thresholds:
            count = sum(1 for t, _ in user_deque if now - t <= timeframe)
            if count >= threshold:
                return f"{count} messages in {timeframe.seconds} seconds"
        
        # Check repeated messages
        recent_hashes = [h for t, h in user_deque if now - t <= self.repeat_timeframe]
        hash_count = defaultdict(int)
        for h in recent_hashes:
            hash_count[h] += 1
            if hash_count[h] >= self.repeat_threshold:
                return f"Repeated message spam ({hash_count[h]} times)"
        
        return None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            message.guild is None or
            message.guild.id != guild_id or
            message.author == message.guild.me or
            message.author.guild_permissions.administrator or
            message.channel.id in allowed_channels
        ):
            return

        bypass_role = message.guild.get_role(bypass_role_id)
        if bypass_role and bypass_role in message.author.roles:
            return
        
        if message.reference and isinstance(message.reference.resolved, discord.Message):
            return

        now = datetime.now(timezone.utc)
        user_id = message.author.id
        content_hash = hash(message.content.strip().lower())

        # Append to deque with reasonable maxlen
        user_deque = self.user_message_history[user_id]
        user_deque.append((now, content_hash))


        # Remove stale entries efficiently
        max_timeframe = max(tf for _, tf in self.thresholds + [(0, self.repeat_timeframe)])
        while user_deque and now - user_deque[0][0] > max_timeframe:
            user_deque.popleft()

        # Check for spamming
        spam_reason = self.is_spamming(user_deque, now)
        if spam_reason and not message.author.is_timed_out():
            await self.apply_timeout(message.author, message.channel, now, reason=spam_reason)
            user_deque.clear()  # clear history after timeout

    async def apply_timeout(self, member: discord.Member, channel: discord.abc.GuildChannel, now: datetime, reason: str):
        until = now + self.timeout_duration
        try:
            await member.timeout(until, reason=f"Antispam: {reason}")
            embed = discord.Embed(
                title="Antispam Triggered",
                description=f"{member.mention} has been timed out for **{reason}**.",
                color=discord.Color.red(),
                timestamp=now
            )

            log_channel = member.guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            await channel.send(embed=embed)

        except Exception as e:
            print(f"[Antispam Error]: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiSpam(bot))
