from discord.ext import commands

class Vanity(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Utility"
    
    @commands.command(name="vanity", description="Gives the vanity url of the server if available")
    @commands.guild_only()
    async def vanity(self, ctx: commands.Context):
        vanity_url_code = ctx.guild.vanity_url_code
        if vanity_url_code:
            if ctx.author.guild_permissions.manage_guild:
                vanity_invite = await ctx.guild.vanity_invite()
                uses = vanity_invite.uses
                return await ctx.reply(f"🔗 **Vanity URL:** discord.gg/{vanity_url_code}\n👥 **Uses:** {uses}", mention_author=False)
            await ctx.reply(f"🔗 **Vanity URL:** discord.gg/{vanity_url_code}", mention_author=False)
        else:
            await ctx.reply("This server does not have a vanity url", mention_author = False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Vanity(bot))