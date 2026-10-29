import discord
from discord.ext import commands
from datetime import datetime, timezone
from utils.emotes import get_emoji

class Whois(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"

    @commands.hybrid_command(name="whois", description="Get information about a server member.", aliases=["userinfo"])
    @commands.guild_only()
    async def whois(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            member = member or ctx.author

            user = member._user if hasattr(member, "_user") else member  # for lazy member

            created = discord.utils.format_dt(member.created_at, style="F")
            created_rel = discord.utils.format_dt(member.created_at, style="R")
            joined = discord.utils.format_dt(member.joined_at, style="F") if member.joined_at else "Unknown"
            joined_rel = discord.utils.format_dt(member.joined_at, style="R") if member.joined_at else "Unknown"

            status = str(member.status).title()
            boost_info = "Boosting since " + discord.utils.format_dt(member.premium_since, style="R") if member.premium_since else "Not boosting"

            roles = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]
            role_display = ", ".join(roles) if roles else "None"
            if len(role_display) > 1024:
                role_display = f"{', '.join(roles[:10])}... and {len(roles)-10} more"
            
            top_role = member.top_role.mention if member.top_role else "None"

            embed = discord.Embed(
                title=f"User Info - {member.display_name}",
                timestamp=datetime.now(timezone.utc)
            )

            embed.set_thumbnail(url=member.display_avatar.url if member.avatar else member.default_avatar.url)
            u = await self.bot.fetch_user(member.id)
            if u.banner:
                embed.set_image(url=u.banner.url)
                
            embed.add_field(name="Username", value=f"{member} (`{member.id}`)", inline=False)
            embed.add_field(name="Account Created", value=f"{created} ({created_rel})", inline=True)
            embed.add_field(name="Joined Server", value=f"{joined} ({joined_rel})", inline=True)
            embed.add_field(name="Top Role", value=top_role, inline=True)
            embed.add_field(name="Status", value=f"{get_emoji(str(member.status))} {status}", inline=True)
            if hasattr(member, "status") and hasattr(member, "mobile_status"):
                devices = []
                if member.desktop_status != discord.Status.offline:
                    devices.append("Desktop")
                if member.web_status != discord.Status.offline:
                    devices.append("Web")
                if member.mobile_status != discord.Status.offline:
                    devices.append("Mobile")
                if devices:
                    embed.add_field(name="Active On", value=", ".join(devices), inline=True)
            if not member.bot:        
                embed.add_field(name="Boost Status", value=boost_info, inline=True)
            embed.add_field(name="Roles", value=role_display, inline=False)


            user_perms = member.guild_permissions
            basic = [name.replace("_", " ").title() for name, value in user_perms if value and name in basic_perms]
            mod = [name.replace("_", " ").title() for name, value in user_perms if value and name in mod_perms]

            if basic:
                embed.add_field(name="Basic Permissions", value=", ".join(basic), inline=False)
            if mod:
                embed.add_field(name="Mod Permissions", value=", ".join(mod), inline=False)
            if not (basic or mod):
                embed.add_field(name="Permissions", value="None", inline=False)

            await ctx.send(embed=embed)

basic_perms = {
    "create_instant_invite",
    "add_reactions",
    "priority_speaker",
    "stream",
    "read_messages",  # legacy: equivalent to "view_channel"
    "send_messages",
    "send_tts_messages",
    "embed_links",
    "attach_files",
    "read_message_history",
    "mention_everyone",
    "external_emojis",
    "external_stickers",
    "connect",
    "speak",
    "use_voice_activation",
    "change_nickname",
    "use_application_commands",
    "request_to_speak",
    "create_public_threads",
    "create_private_threads",
    "send_messages_in_threads",
    "use_embedded_activities",
    "use_soundboard",
    "create_expressions",
    "use_external_sounds",
    "send_voice_messages",
    "send_polls",
    "use_external_apps",
}

mod_perms = {
    "kick_members",
    "ban_members",
    "administrator",
    "manage_channels",
    "manage_guild",  # manage server
    "view_audit_log",
    "view_guild_insights",
    "mute_members",
    "deafen_members",
    "move_members",
    "manage_nicknames",
    "manage_roles",
    "manage_webhooks",
    "manage_expressions",
    "manage_events",
    "manage_threads",
    "moderate_members",  # timeout
    "view_creator_monetization_analytics",
    "create_events",
}


async def setup(bot: commands.Bot):
    await bot.add_cog(Whois(bot))
