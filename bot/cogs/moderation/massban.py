import discord
from discord.ext import commands
from utils.emotes import get_emoji

class MassBanView(discord.ui.View):
    def __init__(self, ctx, members_to_ban, reason):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.members_to_ban = members_to_ban
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
            description=f"{crossmark} Mass ban cancelled.",
            color=discord.Color.lighter_grey()
        )
        return await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        banned = 0
        skipped = 0
        crossmark = get_emoji("crossmark")
        checkmark = get_emoji("checkmark")
        for member in self.members_to_ban:
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
                await member.ban(reason=f"massban requested by {self.ctx.author}")
                banned += 1
            except Exception:
                skipped += 1

        embed = discord.Embed(
            title=f"{checkmark} Mass Ban Complete",
            description=f"Banned: `{banned}`\nSkipped: `{skipped}`",
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

class MassBan(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"

    @commands.hybrid_command(name="massban", description="Ban multiple members from the server safely.")
    @discord.app_commands.describe(
        members="Mention multiple members to ban",
        reason="Reason for the ban (optional)"
    )
    @commands.guild_only()
    async def massban(self, ctx: commands.Context, members: commands.Greedy[discord.Member], *, reason: str = "No reason provided"):
        if ctx.interaction:
            await ctx.defer()

        crossmark = get_emoji("crossmark")

        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Administrator** permission to use this command."))

        if not ctx.guild.me.guild_permissions.ban_members:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} I need **Ban Members** permission."))

        if not members:
            return await ctx.send(embed=discord.Embed(description=f"{crossmark} Please mention the members you want to ban."))

        member_mentions = "\n".join([member.mention for member in members])
        embed = discord.Embed(
            title="⚠️ Confirm Mass Ban",
            description=f"You are about to ban `{len(members)}` members:\n{member_mentions}\n\nReason: `{reason}`\n\nDo you confirm?",
            color=discord.Color.orange()
        )

        view = MassBanView(ctx, members, reason)
        view.message = await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(MassBan(bot))
