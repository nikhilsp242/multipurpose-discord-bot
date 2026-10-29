import discord
from discord.ext import commands
from utils.emotes import get_emoji
from models.roles import Roles
from utils.getdata import bdayRoleAvailable
from utils.getdata import bdayChannelAvailable
from models.channels import Channel
class BirthdaySettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Birthday"
    
    @commands.hybrid_command(
        name="setup-birthdays",
        description="Set the role and/or channel used for birthday messages.",
        aliases=["setupbday", "birthdaysetup"]
    )
    @commands.guild_only()
    @discord.app_commands.describe(
        channel="Channel where birthday wishes will be sent",
        role="Role to assign on a user's birthday"
    )
    async def setup_birthdays(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        role: discord.Role = None
    ):
        if ctx.interaction:
            await ctx.defer()

        async with ctx.typing():
            guild_id = str(ctx.guild.id)
            bot_member = ctx.guild.me
            crossmark = get_emoji("crossmark")
            checkmark = get_emoji("checkmark")
            blobcat = get_emoji("blobcatred")

            if not ctx.author.guild_permissions.manage_roles and role:
                return await ctx.send(embed=discord.Embed(
                    description=f"{crossmark} You need **Manage Roles** permission to set the birthday role."
                ))
            if not ctx.author.guild_permissions.manage_channels and channel:
                return await ctx.send(embed=discord.Embed(
                    description=f"{crossmark} You need **Manage Channels** permission to set the birthday channel."
                ))

            embed = discord.Embed(title="Birthday Setup")
            embed.set_thumbnail(url=ctx.guild.me.avatar.url)

            # Handle role setup
            if role:
                if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                    return await ctx.send(embed=discord.Embed(
                        description=f"{crossmark} Please choose a role below your top role."
                    ))
                if not ctx.guild.me.guild_permissions.manage_roles:
                    return await ctx.send(embed=discord.Embed(
                        description=f"{crossmark} I need **Manage Roles** permission to assign roles."
                    ))
                if role >= bot_member.top_role:
                    return await ctx.send(embed=discord.Embed(
                        description=f"{crossmark} I can't assign the role {role.mention}. "
                                    f"Please hoist my role or choose a lower role."
                    ))

                role_id = str(role.id)
                bday_role_available = bdayRoleAvailable(guild_id)
                if bday_role_available == role_id:
                    embed.add_field(name="Birthday Role", value=f"{blobcat} {role.mention} is already set.", inline=False)
                else:
                    if bday_role_available:
                        current = Roles.get_role_to_edit(guild_id, bday_role_available)
                        current.is_bday_role = False
                        current.save()

                    new = Roles.get_role_to_save(guild_id)
                    new.role_id = role_id
                    new.role_name = role.name
                    new.is_bday_role = True
                    new.save()
                    embed.add_field(name="Birthday Role", value=f"{checkmark} Set to {role.mention}", inline=False)

            # Handle channel setup
            if channel:
                permissions = channel.permissions_for(bot_member)
                required_perms = ["send_messages", "embed_links", "view_channel"]
                missing = [perm.replace("_", " ").title() for perm in required_perms if not getattr(permissions, perm)]
                if missing:
                    return await ctx.send(embed=discord.Embed(
                        description=f"{crossmark} I'm missing these permissions in {channel.mention}: {', '.join(missing)}."
                    ))

                channel_id = str(channel.id)
                bday_channel_available = bdayChannelAvailable(guild_id)
                if bday_channel_available == channel_id:
                    embed.add_field(name="Birthday Channel", value=f"{blobcat} Already set to {channel.mention}.", inline=False)
                else:
                    if bday_channel_available:
                        current = Channel.get(bday_channel_available, guild_id)
                        current.is_bday_channel = False
                        current.save()

                    new = Channel.get(channel_id, guild_id)
                    new.name = channel.name
                    new.is_bday_channel = True
                    new.save()
                    embed.add_field(name="Birthday Channel", value=f"{checkmark} Set to {channel.mention}", inline=False)

            return await ctx.send(embed=embed)

    
async def setup(bot: commands.Bot):
    await bot.add_cog(BirthdaySettings(bot))