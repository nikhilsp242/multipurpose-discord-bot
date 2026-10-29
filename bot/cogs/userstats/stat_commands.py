import discord
from discord.ext import commands
from models.userstats import UserStats
from models.messagecount import MessageCount
from utils.emotes import get_emoji
from utils.time_formating import format_time
from utils.getdata import mainChannelAvailable

class GetUserStat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Stats"
    
    @commands.hybrid_command(name="messages", description="Get total number of messages sent by an user", aliases = ["mes"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to get their total messages")
    async def get_messages(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} This command takes only human members as an argument"))
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            messages = UserStats.get_one(user_id , guild_id).total_messages
            chat = get_emoji("chat")
            embed = discord.Embed(description=f"**{user.display_name}'s** Total Messages : `{messages}` {chat}")
            return await ctx.send(embed=embed)

    @commands.hybrid_command(name="balance", description="Get balance of an user", aliases = ["bal"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to get their balance")
    async def get_balance(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} This command takes only human members as an argument"))
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            balance = UserStats.get_one(user_id , guild_id).balance
            bal = get_emoji("ecoin")
            embed = discord.Embed(description=f"**{user.display_name}'s** Balance : `{balance}` {bal}")
            return await ctx.send(embed=embed)

    @commands.hybrid_command(name="experience-points", description="Get xp of an user", aliases = ["xp"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to get their experience points")
    async def get_xp(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} This command takes only human members as an argument"))
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            xp = UserStats.get_one(user_id , guild_id).xp
            immortal = get_emoji("immortal")
            embed = discord.Embed(description=f"**{user.display_name}'s** XP : `{xp}` {immortal}")
            return await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="level", description="Get level of an user", aliases = ["lvl"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to get their level")
    async def get_level(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} This command takes only human members as an argument"))
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            level = UserStats.get_one(user_id , guild_id).level
            uparrow = get_emoji("uparrow")
            embed = discord.Embed(description=f"**{user.display_name}'s** Level : `{level}` {uparrow}")
            return await ctx.send(embed=embed)

    @commands.hybrid_command(name="replies-received", description="Get the total number of replies received by an user", aliases = ["replies", "rr"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to get their total number of replies received")
    async def get_replies(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} This command takes only human members as an argument"))
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            replies_received = UserStats.get_one(user_id , guild_id).replies_received
            ping = get_emoji("ping")
            embed = discord.Embed(description=f"**{user.display_name}'s** Replies Received : `{replies_received}` {ping}")
            return await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="attachements-sent", description="Get the total number of attachments sent by an user", aliases = ["attachments", "atch", "attach"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to get their total number of attachments sent")
    async def get_attachments(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} This command takes only human members as an argument"))
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            total_attachments = UserStats.get_one(user_id , guild_id).total_attachments
            attachments = get_emoji("attachments")
            embed = discord.Embed(description=f"**{user.display_name}'s** Total Attachments Sent : `{total_attachments}` {attachments}")
            return await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="vc-duration", description="Get the VC duration of an user", aliases = ["vcd", "vctime"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to get their total time spent in Voice Channels")
    async def get_vc_duration(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} This command takes only human members as an argument"))
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            vc_time = UserStats.get_one(user_id , guild_id).vc_time
            vc = get_emoji("vc")
            embed = discord.Embed(description=f"**{user.display_name}'s** Total VC Duration : `{format_time(vc_time)}` {vc}")
            return await ctx.send(embed=embed)
            

    @commands.hybrid_command(name="reputation", description="Get reputation of an user", aliases = ["rep"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to get their reputation")
    async def get_reputation(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} This command takes only human members as an argument"))
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            reputation = UserStats.get_one(user_id , guild_id).reputation
            rep = get_emoji("reputation")
            embed = discord.Embed(description=f"**{user.display_name}'s** Reputation : `{reputation}` {rep}")
            return await ctx.send(embed=embed)

    @commands.hybrid_command(name="main-channel-messages", description="Get total number of messages of an user in main channel", aliases = ["mm"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to get their messages in main channel")
    async def get_main_channel_messages(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} This command takes only human members as an argument"))
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            if not mainChannelAvailable(guild_id):
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} Main Channel is not set for this guild"))
            mm = UserStats.get_one(user_id , guild_id).main_channel_messages
            chat = get_emoji("chat")
            embed = discord.Embed(description=f"**{user.display_name}'s** Total Messages in Main Channel : `{mm}` {chat}")
            return await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="message-summary", description="Get message summary of an user", aliases = ["ms"])
    @commands.guild_only()
    @discord.app_commands.describe(user="Select user to get their message summary")
    async def get_message_summary(self, ctx: commands.Context, user: discord.Member = None):
        if ctx.interaction: await ctx.defer()
        async with ctx.typing():
            if not user:
                user = ctx.author
            if user.bot and user != self.bot.user:
                crossmark = get_emoji("crossmark")
                return await ctx.send(embed=discord.Embed(description=f"{crossmark} This command takes only human members as an argument"))
            user_id = str(user.id)
            guild_id = str(ctx.guild.id)
            ms = MessageCount.get_one(user_id, guild_id)
            chat = get_emoji("chat")
            description=f"""**User : {user.mention}**\n\n🔹Today :**{ms.daily_messages}**{chat}\n🔹This Week : **{ms.weekly_messages}** {chat}\n🔹This Month : **{ms.monthly_messages}** {chat}\n"""
            main_channel = mainChannelAvailable(guild_id)
            if main_channel:
                main_channel = ctx.guild.get_channel(int(main_channel))
                description += f"""\n**In {main_channel.mention}**\n🔸Today :**{ms.daily_main_channel_messages} {chat}**\n🔸This Week :**{ms.weekly_main_channel_messages} {chat}**\n🔸This Month :**{ms.monthly_main_channel_messages} {chat}**"""
            embed = discord.Embed(
                title="Message Summary",
                description=description
                )
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            return await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(GetUserStat(bot))
