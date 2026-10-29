import discord
from discord.ext import commands
from models.warnsettings import WarnSettings
from models.warnings import Warnings
from utils.emotes import get_emoji

class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"

    @commands.command(name="warns", description="Check the number of warns received by an user")
    @commands.guild_only()
    async def warns(self, ctx: commands.Context, user: discord.Member=None):
        async with ctx.typing():
            if not user:
                user = ctx.author
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            return await ctx.send(embed=discord.Embed(description=f"**{user.display_name}'s** Total Warns : {Warnings.get(user_id, guild_id).warns} {get_emoji("warn")}"))

    @commands.hybrid_command(name="setup-warns", description="Setup for warns for this guild", aliases=["setupwarns", "setwarn"])
    @commands.guild_only()
    @discord.app_commands.describe(channel="(Recommended) The channel where the warnings go")
    async def warn_setup(self, ctx: commands.Context, channel: discord.TextChannel):
        if ctx.interaction : await ctx.defer()
        async with ctx.typing():
            crossmark = get_emoji("crossmark")
            if not ctx.author.guild_permissions.manage_channels:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Manage Channels** permission to use this command."))
            
            me = ctx.guild.me
            permissions = channel.permissions_for(me)
            required_perms = ["send_messages", "embed_links", "view_channel"]
            missing = [perm.replace("_", " ").title() for perm in required_perms if not getattr(permissions, perm)]
            if missing:
                return await ctx.send(embed=discord.Embed(
                    description=f"{crossmark} I'm missing these permissions in {channel.mention}: {', '.join(missing)}."
                ))
            guild_id = str(ctx.guild.id)
            warn_settings = WarnSettings.get(guild_id)
            warn_settings.channel_id = channel.id
            warn_settings.channel_name = channel.name
            warn_settings.save()

            return await ctx.send(embed=discord.Embed(description=f"**Target : {channel.mention}**\n{get_emoji("checkmark")} This channel has been set as warn log channel."))
        
    
    @commands.hybrid_command(name="warn", description="Warn an user")
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to warn them", reason="The reason (description) for the warning")
    async def warn(self, ctx: commands.Context, user: discord.Member,* , reason: str):
        if ctx.interaction: await ctx.defer(ephemeral=True)
        async with ctx.typing():
            if not ctx.author.guild_permissions.moderate_members:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("crossmark")} You need **Moderate Members** permission to use this command."), ephemeral=bool(ctx.interaction))
            if user == ctx.author:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} You cannot warn yourself."), ephemeral=bool(ctx.interaction))
            if user == ctx.guild.me:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} Haha. Nice try buddy."), ephemeral=bool(ctx.interaction))
            if user.bot:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} You cannot warn bots."), ephemeral=bool(ctx.interaction))
            if user == ctx.guild.owner:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} You cannot warn the guild owner."), ephemeral=bool(ctx.interaction))
            if user.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("crossmark")} You can only warn members below your top role"), ephemeral=bool(ctx.interaction))
            
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            warn_settings = WarnSettings.get(guild_id)
            user_warns = Warnings.get(user_id, guild_id)
            embed = discord.Embed(
                title="You've been warned!",
                description=f"**{get_emoji("warn")} Warning Number : {user_warns.warns+1}**"
            )
            embed.set_footer(text=f"warned by {ctx.author.name}")
            embed.add_field(name="🛑 Reason", value=reason, inline=False)
            if user_warns.prev_warn:
                embed.add_field(name="Previous Warning", value=user_warns.prev_warn, inline= False)
            sent_message = None
            if warn_settings.channel_id:
                warn_channel = ctx.guild.get_channel(int(warn_settings.channel_id))
                if warn_channel:
                    try:
                        sent_message = await warn_channel.send(user.mention, embed=embed)
                    except discord.Forbidden:
                        pass  # fall back to DM
                    except discord.HTTPException:
                        pass
            if not sent_message:
                try:
                    sent_message = await user.send(embed=embed)
                except discord.Forbidden:
                    return await ctx.send(embed=discord.Embed(
                        description=f"{get_emoji("crossmark")} Couldn't warn {user.mention}. I can't send messages in the warn channel or DM the user."
                    ), ephemeral=bool(ctx.interaction))
            if sent_message:
                user_warns.prev_warn = sent_message.jump_url  # Save message link
                user_warns.warns += 1
                user_warns.save()
                checkmark = get_emoji("checkmark")
                await ctx.send(embed=discord.Embed(description=f"{checkmark} {user.mention} has been warned ➡ {sent_message.jump_url}"), ephemeral=True if ctx.interaction else False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Warn(bot))            