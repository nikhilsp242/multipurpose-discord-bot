import discord
from discord.ext import commands
from utils.emotes import get_emoji

class MassKickView(discord.ui.View):
    def __init__(self, ctx, members_to_kick, reason):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.members_to_kick = members_to_kick
        self.reason = reason
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You cannot interact with this confirmation.", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        crossmark = get_emoji("crossmark")
        embed = discord.Embed(
            description=f"{crossmark} Mass kick cancelled.",
            color=discord.Color.lighter_grey()
        )
        return await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        kicked = 0
        skipped = 0
        crossmark = get_emoji("crossmark")
        checkmark = get_emoji("checkmark")
        for member in self.members_to_kick:
            try:
                if member == self.ctx.guild.owner or member == self.ctx.author:
                    skipped += 1
                    continue
                if member.top_role >= self.ctx.author.top_role and self.ctx.author != self.ctx.guild.owner:
                    skipped += 1
                    continue
                if member.top_role >= self.ctx.guild.me.top_role:
                    skipped += 1
                    continue
                await member.kick(reason=f"masskick requested by {self.ctx.author}")
                kicked += 1
            except Exception:
                skipped += 1

        embed = discord.Embed(
            title=f"{checkmark} Mass Kick Complete",
            description=f"Kicked: `{kicked}`\nSkipped: `{skipped}`",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=self.reason if self.reason else "Not provided")
        return await interaction.message.edit(embed=embed, view=None)

    
    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        try:
            await self.message.edit(view=None)
        except:
            pass


class MassKick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"

    @commands.hybrid_command(name="masskick", description="Kick multiple members from the server safely.")
    @discord.app_commands.describe(
        members="Mention multiple members to kick",
        reason="Reason for the kick (optional)"
    )
    @commands.guild_only()
    async def masskick(self, ctx: commands.Context, members: commands.Greedy[discord.Member], *, reason: str = "No reason provided"):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            crossmark = get_emoji("crossmark")

            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Administrator** permission to use this command."))

            if not members:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} Please mention the members you want to kick."))

            member_mentions = "\n".join([member.mention for member in members])
            embed = discord.Embed(
                title="⚠️ Confirm Mass Kick",
                description=f"You are about to kick `{len(members)}` members:\n{member_mentions}\n\nReason: `{reason}`\n\nDo you confirm?",
                color=discord.Color.orange()
            )

            view = MassKickView(ctx, members, reason)
            view.message = await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(MassKick(bot))
