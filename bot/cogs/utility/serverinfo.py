import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"

    @commands.hybrid_command(
        name="serverinfo",
        description="Display detailed information about this server.",
        aliases=["server-info", "guildinfo"]
    )
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            guild = ctx.guild

            bots = [m for m in guild.members if m.bot]
            humans = [m for m in guild.members if not m.bot]
            online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)

            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            category_channels = len(guild.categories)
            thread_channels = len(guild.threads)
            forum_channels = len([ch for ch in guild.channels if isinstance(ch, discord.ForumChannel)])

            emoji_count = len(guild.emojis)
            animated_emoji_count = sum(1 for e in guild.emojis if e.animated)
            sticker_count = len(guild.stickers)

            verification_level = str(guild.verification_level).replace("_", " ").title()
            locale = str(guild.preferred_locale).replace("_", " ").title()

            created_at = discord.utils.format_dt(guild.created_at, style="F")
            created_at_relative = discord.utils.format_dt(guild.created_at, style="R")

            embed = discord.Embed(
                title=f"Server Information - {guild.name}",
                description=f"Server ID: `{guild.id}`",
                timestamp=datetime.now(timezone.utc)
            )

            # Set icons and banners
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            if guild.banner:
                embed.set_image(url=guild.banner.url)
            elif guild.splash:
                embed.set_image(url=guild.splash.url)

            # Optional Description
            if guild.description:
                embed.add_field(name="Description", value=guild.description, inline=False)

            embed.add_field(name="Owner", value=f"{guild.owner.mention} (`{guild.owner.id}`)", inline=True)
            embed.add_field(name="Created", value=f"{created_at}\n{created_at_relative}", inline=True)
            embed.add_field(name="Preferred Locale", value=locale, inline=True)

            embed.add_field(
                name="Members",
                value=(
                    f"Total: {guild.member_count}\n"
                    f"Humans: {len(humans)}\n"
                    f"Bots: {len(bots)}\n"
                    f"Online: {online_members}"
                ),
                inline=True
            )

            embed.add_field(
                name="Channels",
                value=(
                    f"Text: {text_channels}\n"
                    f"Voice: {voice_channels}\n"
                    f"Categories: {category_channels}\n"
                    f"Threads: {thread_channels}\n"
                    f"Forums: {forum_channels}"
                ),
                inline=True
            )

            embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
            embed.add_field(name="Boost Status", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=False)
            embed.add_field(name="Verification Level", value=verification_level, inline=False)

            embed.add_field(name="Emojis", value=f"Total: {emoji_count} (Animated: {animated_emoji_count})", inline=False)
            embed.add_field(name="Stickers", value=f"{sticker_count}", inline=False)

            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerInfo(bot))
