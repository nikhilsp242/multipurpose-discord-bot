import discord
from discord.ext import commands
from utils.emotes import get_emoji
from datetime import datetime , timezone
import asyncio
import json

my_guild_id = 1183064183646982164
BUMP_INTERVAL = 5
bump_data_path = "data/bump_data.json"
bump_role_id = 1252016053584658442
bump_channel_id = 1385387123053564004 #1252219365147934801

class BumpReminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bump_message = None
        self.reminder_timer = None
        for command in self.get_commands():
            command.cog_category = "Utility"
    
    @commands.command(name="bumprole", description="Get notified for bumping, expects `add` or `remove` arguments")
    @commands.guild_only()
    async def bumprole(self, ctx: commands.Context, action: str):
        if ctx.guild.id != my_guild_id:
            return
        bump_role = ctx.guild.get_role(bump_role_id)
        if not bump_role:
            await ctx.reply("couldn't find bump role", mention_author=False)
        if action.lower() == "add":
            await ctx.author.add_roles(bump_role)
            await ctx.reply("You will be notified for bumping", mention_author=False)
        elif action.lower() == "remove":
            await ctx.author.remove_roles(bump_role)
            await ctx.reply("You will not be notified for bumping", mention_author=False)
    
    @commands.Cog.listener()
    async def on_ready(self):
        reminder = self.load_reminder()
        if reminder:
            bump_timestamp = datetime.fromisoformat(reminder['bump_timestamp'])
            elapsed_time = (datetime.now(timezone.utc) - bump_timestamp).total_seconds()
            remaining_time = BUMP_INTERVAL - elapsed_time
            if remaining_time > 0:
                asyncio.create_task(self.remind_bump(self.bot.get_channel(bump_channel_id), remaining_time))
            print("✅ Bump reminder loaded and countdown continued.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild.id != my_guild_id:
            return
        if message.author.id == 1194815627324571668:
            print(1)
            # if message.embeds:
            #     description = message.embeds[0].description
            if 'Bump done!' in message.content:  
                print(2)
                done = get_emoji("checkmark")
                bell = get_emoji("bell")
                if self.bump_message:
                    await self.bump_message.delete()
                embed = discord.Embed(title=f"Bump Notification {bell}", description="Use the command `bumprole` to be notified\n**Example usage:**\n`bumprole add`\n`bumprole remove`")
                self.bump_message = await message.reply(f"Bump done {done}", embed=embed)
                await self.handle_bump_command(message)
        
    async def handle_bump_command(self, message:discord.Message):
        try:
            if self.reminder_timer:
                self.reminder_timer.cancel()
            bump_timestamp = datetime.now(timezone.utc).isoformat()
            self.save_reminder(bump_timestamp)
            self.reminder_timer = asyncio.create_task(self.remind_bump(message.channel, BUMP_INTERVAL))
        except Exception as e:
            print(f"Error saving bump timestamp : {e}")

    async def remind_bump(self, channel:discord.TextChannel, countdown):
        try:
            bump_role = channel.guild.get_role(bump_role_id)
            await asyncio.sleep(countdown)
            await channel.send(f"It's time to {bump_role.mention} again")
            self.delete_reminder()
        except Exception as e:
            print(f"Failed to remind bumping : {e}")
        finally:
            self.reminder_timer = None
    
    def load_reminder(self):
        try:
            with open(bump_data_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError):
            return None

    def save_reminder(self, bump_timestamp):
        with open(bump_data_path, 'w') as f:
            json.dump({'bump_timestamp': bump_timestamp}, f)
        
    def delete_reminder(self):
        with open(bump_data_path, 'w') as f:
            json.dump({}, f)

async def setup(bot: commands.Bot):
    await bot.add_cog(BumpReminder(bot))