import discord
from discord.ext import commands
from discord.ui import View , Button


class AvatarBannerView(View):
    def __init__(self, ctx, member, server,  avatar_url , banner_url , server_avatar_url):
        super().__init__(timeout=120)
        self.member = member
        self.server = server
        self.ctx = ctx
        self.avatar_url = avatar_url
        self.banner_url = banner_url
        self.server_avatar_url = server_avatar_url
        self.message = None
        
        if not banner_url:
            self.children[1].disabled = True
        if not server_avatar_url:
            self.children[2].disabled = True 
            self.remove_item(self.children[2])   

    def set_message(self, message):
        self.message = message

    async def interaction_check(self, interaction : discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(f"This avatar menu is controlled by {self.ctx.author.mention}.", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="Avatar", style=discord.ButtonStyle.green)
    async def show_avatar(self , interaction: discord.Interaction, button : Button):
        display_name = (self.member.global_name or self.member.name) if self.member else self.server.name
        embed = discord.Embed(title="Avatar" , description=f"[Avatar URL]({self.avatar_url})")
        embed.set_author(name=f"{display_name}", icon_url=self.avatar_url)
        embed.set_image(url=self.avatar_url)
        embed.set_footer(text=f"Requested by {self.ctx.author.name}", icon_url=self.ctx.author.avatar.url)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Banner", style=discord.ButtonStyle.green)
    async def show_banner(self, interaction : discord.Interaction, button : Button):
        display_name = (self.member.global_name or self.member.name) if self.member else self.server.name
        embed = discord.Embed(title="Banner" , description=f"[Banner URL]({self.banner_url})")
        embed.set_author(name=f"{display_name}", icon_url=self.avatar_url)
        embed.set_image(url=self.banner_url)
        embed.set_footer(text=f"Requested by {self.ctx.author.name}", icon_url=self.ctx.author.avatar.url)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Server Avatar", style=discord.ButtonStyle.secondary)
    async def show_server_avatar(self, interaction : discord.Interaction, button : Button):
        embed = discord.Embed(title="Server Avatar" , description=f"[Server Avatar]({self.server_avatar_url})")
        embed.set_author(name=f"{self.member.display_name}", icon_url=self.server_avatar_url)
        embed.set_image(url=self.server_avatar_url)
        embed.set_footer(text=f"Requested by {self.ctx.author.name}", icon_url=self.ctx.author.avatar.url)
        await interaction.response.edit_message(embed=embed)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
        except Exception as e:
            pass

class Avatar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"
    
    @commands.command(name="avatar", description="Get avatar of an user or guild icon", aliases=["av", "pfp"])
    @commands.guild_only()
    async def avatar(self, ctx: commands.Context, target=None, **_):
        if not target:
            target = ctx.author
        elif target.lower() not in ["server", "guild"]:
            try:
                target = await commands.MemberConverter().convert(ctx, target)
            except discord.ext.commands.errors.MemberNotFound:
                await ctx.message.reply(f"Member not found.", mention_author=False)
                return

        if isinstance(target, discord.Member):
            try:
                avatar_url = target.avatar.url if target.avatar else target.default_avatar.url
                banner_url = None

                server_avatar_url = target.display_avatar.url if target.display_avatar else None
                

                user = await self.bot.fetch_user(target.id)
                if user.banner:
                    banner_url = user.banner.url
                    
                main_display_name = target.global_name or target.name
                

                embed = discord.Embed(title="Avatar", description=f"[Avatar URL]({avatar_url})")
                embed.set_author(name=f"{main_display_name}", icon_url=avatar_url)
                embed.set_image(url=avatar_url)
                embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

                view = AvatarBannerView(ctx, target, None, avatar_url, banner_url, server_avatar_url)
                message = await ctx.reply(embed=embed, view=view, mention_author=False)
                view.set_message(message)
                return
            except discord.ext.commands.errors.MemberNotFound:
                await ctx.message.reply(f"Member {target} not found.", mention_author=False)
                return
        else:
            guild = ctx.guild
            avatar_url = guild.icon.url if guild.icon else None
            banner_url = guild.banner.url if guild.banner else None
            embed = discord.Embed(title="Avatar" , description=f"[Avatar URL]({avatar_url})")
            embed.set_author(name=f"{guild.name}", icon_url=avatar_url)
            embed.set_image(url=avatar_url)
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
            view = AvatarBannerView(ctx, None, guild, avatar_url, banner_url , None)
            message = await ctx.reply(embed=embed,view=view, mention_author = False)
            view.set_message(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Avatar(bot))