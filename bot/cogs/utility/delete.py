import discord
from discord.ext import commands
import typing
from utils.emotes import get_emoji
from discord.ui import View , Button

class ConfirmDelete(View):
    def __init__(self, ctx: commands.Context, target: typing.Union[discord.abc.GuildChannel, discord.Emoji, discord.Role, discord.Invite]):
        super().__init__(timeout=60)
        self.target = target
        self.ctx = ctx
        self.message = None
        self.interacted = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You cannot interact with this confirmation.", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        self.interacted = True
        embed = discord.Embed(title="Deletion Cancelled", description=f'The deletion of target has been cancelled.', color=discord.Color.lighter_grey())
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        self.interacted = True
        try:
            await self.target.delete()
        except discord.Forbidden:
            await interaction.response.edit_message(embed=discord.Embed(description=f"{get_emoji('nyaSob')} I do not have permission to delete this target."), view=None)
            return
        except discord.HTTPException as e:
            await interaction.response.edit_message(embed=discord.Embed(description=f"{get_emoji('blobcatred')} Deletion failed: {e}"))
            return    
        checkmark = get_emoji("checkmark")
        crossmark = get_emoji("crossmark")
        if isinstance(self.target, discord.abc.GuildChannel):
            result = f'{checkmark} Channel **{self.target.name}** has been deleted.'
        elif isinstance(self.target, (discord.Emoji)):
            result = f'{checkmark} Emoji **{self.target.name}** has been deleted.'
        elif isinstance(self.target, discord.Role):
            result = f'{checkmark} Role **{self.target.name}** has been deleted.'
        elif isinstance(self.target, discord.Invite):
            result = f'{checkmark} Invite **{self.target.code}** has been deleted.'
        else:
            result = f'{crossmark} Deletion failed. No valid target found.'
        if self.target != self.ctx.channel:
            embed = discord.Embed(title="Deletion Result", description=result, color=discord.Color.red())
            await interaction.response.edit_message(embed=embed, view=None)
    
    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        try:
            await self.message.edit(view=None) if self.interacted else await self.message.edit(view=self)
        except:
            pass


class Delete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"
    
    @commands.command(name="delete", description="Delete any target object", aliases=["del"])
    @commands.guild_only()
    async def delete(self, ctx: commands.Context, target: typing.Union[discord.abc.GuildChannel, discord.Emoji, discord.Role, discord.Invite]):
        async with ctx.typing():
            is_emoji = False
            is_invite = False
            if isinstance(target, discord.Emoji) and target.guild == ctx.guild:
                if not ctx.author.guild_permissions.manage_emojis_and_stickers:
                    return await ctx.send(embed=discord.Embed(description=f"**Target Emoji**\n# {target}\n{get_emoji("crossmark")} You need **Manage Emojis and Stickers** permission to delete this target."))
                is_emoji = True
            elif isinstance(target, discord.abc.GuildChannel) and target.guild == ctx.guild:
                if not ctx.author.guild_permissions.manage_channels:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {target.mention}**\n{get_emoji("crossmark")} You need **Manage Channels** permission to delete this target."))
            elif isinstance(target, discord.Role) and target.guild == ctx.guild:
                if not ctx.author.guild_permissions.manage_roles:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {target.mention}**\n{get_emoji("crossmark")} You need **Manage Roles** permission to delete this target."))
                if ctx.author != ctx.guild.owner and ctx.author.top_role <= target:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {target.mention}**\n{get_emoji("blobcatred")} You can only manage roles below your top role."))
            elif isinstance(target, discord.Invite) and target.guild == ctx.guild:
                if target.code and target.guild != ctx.guild:
                    return
                if not ctx.author.guild_permissions.manage_guild:
                    return await ctx.send(embed=discord.Embed(description=f"**Target : {target.code}**\n{get_emoji("crossmark")} You need **Manage Server** permission to delete this target."))
                is_invite = True
            else:
                return
                # return await ctx.send(embed=discord.Embed(description=f"{get_emoji("blobcatred")} No valid target detected for deletion."), delete_after=5)
            target_mention = None
            if is_emoji:
                target_mention = f"this emoji?\n# {target}"
            elif is_invite:
                target_mention = f"invite :  https://discord.gg/{target.code} ?"
            else:
                target_mention = f"{target.mention} ?"
            embed = discord.Embed(title="Confirm Deletion", description=f"Are you sure you want to delete {target_mention}", color=discord.Color.red())
            view = ConfirmDelete(ctx, target)
            view.message = await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Delete(bot))