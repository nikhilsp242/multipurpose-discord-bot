import discord
from discord.ext import commands
from discord.ui import View, Button
from typing import List
from utils.emotes import get_emoji

class MembersInRoleView(View):
    def __init__(self, ctx: commands.Context, author: discord.Member, role: discord.Role, members: List[discord.Member], per_page: int = 25):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.author = author
        self.role = role
        self.members = members
        self.per_page = per_page
        self.page = 0
        self.message = None
        self.update_buttons()

    def update_buttons(self):
        self.prev.disabled = self.page == 0
        self.next.disabled = (self.page + 1) * self.per_page >= len(self.members)

    def create_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        page_members = self.members[start:end]

        embed = discord.Embed(
            title=f"{len(self.members)} members in {self.role.name}",
            description="\n".join(f"{i + 1 + start}. {member.mention} ({member.name})" for i, member in enumerate(page_members)) or "No members found."
        )
        embed.set_footer(text=f"Page {self.page + 1}/{(len(self.members) - 1) // self.per_page + 1}")
        return embed

    async def send(self):
        embed = self.create_embed()
        if self.ctx.interaction:
            self.message = await self.ctx.interaction.followup.send(embed=embed, view=self, wait=True)
        else:
            self.message = await self.ctx.send(embed=embed, view=self)

    @discord.ui.button(label="⬅ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.author:
            await interaction.response.send_message(f"{get_emoji("blobcatred")} This role menu is controlled by {self.author.mention}", ephemeral=True)
            return
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.author:
            await interaction.response.send_message(f"{get_emoji("blobcatred")} This role menu is controlled by {self.author.mention}", ephemeral=True)
            return
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True
        if self.message:
            await self.message.edit(view=self)


class MemberTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"

    @commands.hybrid_command(name="membersinrole", description="View members with a given role.", aliases=["meminrole"])
    @commands.guild_only()
    async def members_in_role(self, ctx: commands.Context, role: discord.Role):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.manage_roles:
                return await ctx.send(embed=discord.Embed(description=f"{get_emoji("crossmark")} You need `Manage Roles` permission to use this command."))
            members = [m for m in role.members]
            view = MembersInRoleView(ctx, ctx.author, role, members)
            await view.send()


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberTools(bot))
