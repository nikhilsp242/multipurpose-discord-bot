import discord
import discord.app_commands
from discord.ext import commands
from models.levelup import LevelUpConfig
import typing
from utils.emotes import get_emoji
from utils.modifydata import modify_column

class LevelUpSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Settings"
    
    @commands.hybrid_command(name="setup-level-up", description = "Setup level up for this guild", aliases = ["setuplvl","enablelvlup", "enlvlup"])
    @commands.guild_only()
    @discord.app_commands.describe(
        level_up_channel = "Channel for sending level up messages",
        enable_vc_levelup = "(Recommended) Enable XP for voice channels",
    )
    async def enable_levelup(self, ctx: commands.Context, level_up_channel: discord.TextChannel, enable_vc_levelup: typing.Literal["yes", "no"]):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.administrator:
                crossmark = get_emoji("crossmark")
                return await ctx.send(
                    embed=discord.Embed(description=f"{crossmark} You need **Administrator** permission to use this command.")
                )
            bot_member = ctx.guild.me
            perms = level_up_channel.permissions_for(bot_member)
            required_perms = ["send_messages", "embed_links", "view_channel"]
            missing = [perm.replace("_", " ").title() for perm in required_perms if not getattr(perms, perm)]

            if missing:
                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{crossmark} I am missing the following permissions in {level_up_channel.mention}: {', '.join(missing)}."
                    )
                )
            
            guild_id = str(ctx.guild.id)
            levelupsettings = LevelUpConfig.get(guild_id)
            greenline =  get_emoji("blobcatred")
            checkmark = get_emoji("checkmark")
            if levelupsettings.levelup_enabled:
                return await ctx.send(embed=discord.Embed(description=f"{greenline} Level Up is already enabled for this guild."))
            levelupsettings.levelup_enabled = True
            levelupsettings.levelup_channel = str(level_up_channel.id)
            levelupsettings.vc_levelup_enabled = True if enable_vc_levelup == "yes" else False
            levelupsettings.save()
            return await ctx.send(embed=discord.Embed(description=f"{checkmark} Level Up has been enabled for this guild."))
    
    @commands.hybrid_command(name="disable-levelup", description = "disable level up for this guild", aliases = ["disablelvlup", "dislvlup"])
    @commands.guild_only()
    async def disable_levelup(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.administrator:
                crossmark = get_emoji("crossmark")
                return await ctx.send(
                    embed=discord.Embed(description=f"{crossmark} You need **Administrator** permission to use this command.")
                )
            guild_id = str(ctx.guild.id)
            levelupsettings = LevelUpConfig.get(guild_id)
            greenline =  get_emoji("blobcatred")
            checkmark = get_emoji("checkmark")
            if not levelupsettings.levelup_enabled:
                return await ctx.send(embed=discord.Embed(description=f"{greenline} Level Up is already disabled for this guild."))
            levelupsettings.levelup_enabled = False
            levelupsettings.vc_levelup_enabled = False
            levelupsettings.save()
            return await ctx.send(embed=discord.Embed(description=f"{checkmark} Level Up has been disabled for this guild."))
    
    @commands.hybrid_command(name="xp-for-all-channels", description = "Enable or Disable xp for all channels in this guild", aliases = ["xpall"])
    @commands.guild_only()
    @discord.app_commands.describe(toggle="Enable or disable XP gain for all channels")
    async def toggle_xp_all(self, ctx: commands.Context, toggle: typing.Literal["enable", "disable"]):
        if ctx.interaction:
            await ctx.defer()

        async with ctx.typing():
            crossmark = get_emoji("crossmark")
            checkmark = get_emoji("checkmark")
            blobcatred = get_emoji("blobcatred")

            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Administrator** permission to use this command."))

            guild_id = str(ctx.guild.id)
            levelupsettings = LevelUpConfig.get(guild_id)

            new_value = True if toggle.lower() == "enable" else False
            already_set = levelupsettings.enable_xp_for_all_channels

            if already_set == new_value:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} XP is already {toggle}d for all channels in this guild."))

            levelupsettings.enable_xp_for_all_channels = new_value
            levelupsettings.save()

            modify_column("channels", guild_id, "isXPChannel", new_value)

            return await ctx.send(embed=discord.Embed(description=f"{checkmark} XP has been **{toggle}d** for all channels in this guild."))
    
    
    @commands.hybrid_command(
        name="coins-for-all-channels",
        description="Enable or disable coins for all channels in this guild",
        aliases=["coinsall"]
    )
    @commands.guild_only()
    @discord.app_commands.describe(toggle="Enable or disable coin for all channels")
    async def toggle_coins_all(self, ctx: commands.Context, toggle: typing.Literal["enable", "disable"]):
        if ctx.interaction:
            await ctx.defer()

        async with ctx.typing():
            crossmark = get_emoji("crossmark")
            checkmark = get_emoji("checkmark")
            blobcatred = get_emoji("blobcatred")

            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} You need **Administrator** permission to use this command."))

            guild_id = str(ctx.guild.id)
            levelupsettings = LevelUpConfig.get(guild_id)

            new_value = True if toggle.lower() == "enable" else False
            already_set = levelupsettings.enable_coins_for_all_channels

            if already_set == new_value:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} Coins are already {toggle}d for all channels in this guild."))

            levelupsettings.enable_coins_for_all_channels = new_value
            levelupsettings.save()
            modify_column("channels", guild_id, "isCoinChannel", new_value)

            return await ctx.send(embed=discord.Embed(description=f"{checkmark} Coins have been **{toggle}d** for all channels in this guild."))
    
    
    @commands.hybrid_command(name="set-booster-xp", description= "Set a xp multiplier for server boosters of this guild", aliases = ["setboostxp", "setboosterxp"])
    @commands.guild_only()
    @discord.app_commands.describe(multiplier = "Choose a xp multiplier value in the range 1-10 (exclusive)")
    async def set_xp_multiplier(self, ctx: commands.Context, multiplier: int):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.administrator:
                crossmark = get_emoji("crossmark")
                return await ctx.send(
                    embed=discord.Embed(description=f"{crossmark} You need **Administrator** permission to use this command.")
                )
            blobcatred = get_emoji("blobcatred")
            if not multiplier:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} Please specify a multiplier value."))
            if multiplier > 10:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} Please specify a value in the `1-10`."))
            if multiplier < 1:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} Please specify a value in the `1-10`."))
        
            guild_id = str(ctx.guild.id)
            levelupsettings = LevelUpConfig.get(guild_id)
            checkmark = get_emoji("checkmark")
            levelupsettings.booster_xp_multiplier = multiplier
            levelupsettings.save()
            return await ctx.send(embed=discord.Embed(description=f"{checkmark} Booster XP multiplier has been set to `{multiplier}` for this guild"))
    
    @commands.hybrid_command(name="set-booster-coins", description= "Set a coins multiplier for server boosters of this guild", aliases = ["setboostcoins", "setboostercoins"])
    @commands.guild_only()
    @discord.app_commands.describe(multiplier = "Choose a coins multiplier value in the range 1-10 (exclusive)")
    async def set_coins_multiplier(self, ctx: commands.Context, multiplier: int):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.administrator:
                crossmark = get_emoji("crossmark")
                return await ctx.send(
                    embed=discord.Embed(description=f"{crossmark} You need **Administrator** permission to use this command.")
                )
            blobcatred = get_emoji("blobcatred")
            if not multiplier:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} Please specify a multiplier value."))
            if multiplier > 10:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} Please specify a value in the `1-10`."))
            if multiplier < 1:
                return await ctx.send(embed=discord.Embed(description=f"{blobcatred} Please specify a value in the `1-10`."))
            
            guild_id = str(ctx.guild.id)
            levelupsettings = LevelUpConfig.get(guild_id)
            checkmark = get_emoji("checkmark")
            levelupsettings.booster_coin_multiplier = multiplier
            levelupsettings.save()
            return await ctx.send(embed=discord.Embed(description=f"{checkmark} Booster XP multiplier has been set to `{multiplier}` for this guild"))
    
    @commands.hybrid_command(name="vc-levelup", description = "Toggle vc level up for this guild", aliases = ["vclvlup", "vclevelup"])
    @commands.guild_only()
    @discord.app_commands.describe(toggle="Enable or Disable VC XP for this this guild")
    async def enable_vc_levelup(self, ctx: commands.Context, toggle: typing.Literal["enable", "disable"]):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.administrator:
                crossmark = get_emoji("crossmark")
                return await ctx.send(
                    embed=discord.Embed(description=f"{crossmark} You need **Administrator** permission to use this command.")     
                )
            guild_id = str(ctx.guild.id)
            levelupsettings = LevelUpConfig.get(guild_id)
            checkmark = get_emoji("checkmark")
            blobcat = get_emoji("blobcatred")
            new_value = True if toggle.lower() == "enable" else False
            if levelupsettings.vc_levelup_enabled == new_value:
                return await ctx.send(embed=discord.Embed(description=f"{blobcat} VC Level Up is already {toggle}d."))
            levelupsettings.vc_levelup_enabled = new_value
            levelupsettings.save()
            return await ctx.send(embed=discord.Embed(description=f"{checkmark} VC Level Up has been **{toggle}d** for this guild."))
    
    @commands.hybrid_command(name="custom-levelup-system", description="Toggle custom level up system", aliases=["customlvlup"])
    @commands.guild_only()
    @discord.app_commands.describe(toggle="Enable or Disable custom level up system for this this guild")
    async def custom_lvlup(self, ctx: commands.Context, toggle: typing.Literal["enable", "disable"]):
        if ctx.interaction:
            await ctx.defer()
        async with ctx.typing():
            if not ctx.author.guild_permissions.administrator:
                crossmark = get_emoji("crossmark")
                return await ctx.send(
                    embed=discord.Embed(description=f"{crossmark} You need **Administrator** permission to use this command.")     
                )
            guild_id = str(ctx.guild.id)
            levelupsettings = LevelUpConfig.get(guild_id)
            checkmark = get_emoji("checkmark")
            blobcat = get_emoji("blobcatred")
            new_value = True if toggle.lower() == "enable" else False
            if levelupsettings.custom_levelup_system == new_value:
                return await ctx.send(embed=discord.Embed(description=f"{blobcat} Custom level up system is already {toggle}d."))
            levelupsettings.custom_levelup_system = new_value
            levelupsettings.save()
            return await ctx.send(embed=discord.Embed(description=f"{checkmark} Custom level up system **{toggle}d** for this guild."))
    
async def setup(bot: commands.Bot):
    await bot.add_cog(LevelUpSettings(bot))