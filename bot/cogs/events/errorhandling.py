import discord
from discord.ext import commands
from discord import app_commands, Interaction
from utils.bot_instance import instance as kaoru
import time
class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        embed = discord.Embed()

        if isinstance(error, app_commands.CommandNotFound):
            embed.title = "❌ Application Command Not Found"
            embed.description = "The command you tried to use does not exist."
        else:
            embed.title = "❌ An Error Occurred"
            embed.description = f"`{str(error)}`"

        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        embed = discord.Embed()

        if isinstance(error, commands.MissingRequiredArgument):
            embed.title = "❌ Missing Required Argument"
            embed.description = f"You missed the required argument: `{error.param.name}`. Please provide it and try again."

        elif isinstance(error, commands.MemberNotFound):
            embed.title = "❌ Member Not Found"
            embed.description = f"Could not find member: `{error.argument}`. Please check and try again."

        elif isinstance(error, commands.CommandNotFound):
            return  # Silently ignore

        elif isinstance(error, commands.BotMissingPermissions):
            missing_perms = ', '.join(error.missing_permissions)
            embed.title = "❌ Missing Permissions"
            embed.description = f"I am missing the following permissions to execute this command:\n`{missing_perms}`."

        elif isinstance(error, commands.CommandOnCooldown):
            retry_time = int(time.time() + error.retry_after)
            embed.title = "⏳ Command On Cooldown"
            embed.description = (
                f"This command is on cooldown.\n"
                f"Try again: <t:{retry_time}:R>"
            )

        elif isinstance(error, commands.NoPrivateMessage):
            embed.title = "❌ Command Not Allowed in DMs"
            embed.description = "This command can only be used in servers, not in private messages."

        elif isinstance(error, commands.BadArgument):
            embed.title = "❌ Bad Argument"
            embed.description = "The arguments provided do not meet the expected requirements. Please check and try again."

        elif isinstance(error, commands.ChannelNotFound):
            embed.title = "❌ Channel Not Found"
            embed.description = "The specified channel could not be found."

        elif isinstance(error, commands.CheckFailure):
            embed.title = "❌ Permission Denied"
            embed.description = "You do not meet the requirements to use this command."

        elif isinstance(error, commands.BadUnionArgument):
            embed.title = "❌ Invalid Argument Type"
            embed.description = (
                "The command received an argument of an invalid type.\n"
                f"Details: `{error.args}`"
            )

        else:
            embed.title = "❌ Unexpected Error"
            embed.description = f"`{str(error)}`"
            owner = kaoru.get_user(kaoru.owner_id)
            if owner:
                try:
                    error_details = (
                        f"⚠️ **Unhandled Error**\n"
                        f"Command: `{ctx.command}`\n"
                        f"User: `{ctx.author}`\n"
                        f"Guild: `{ctx.guild.name if ctx.guild else 'DMs'}`\n"
                        f"Channel: `{ctx.channel}`\n"
                        f"Error: `{str(error)}`"
                    )
                    await owner.send(error_details)
                except discord.Forbidden:
                    pass

        await ctx.reply(embed=embed, mention_author=False, delete_after=5)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
