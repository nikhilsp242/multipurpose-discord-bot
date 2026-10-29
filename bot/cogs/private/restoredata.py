import discord
from discord.ext import commands
import json
import sqlite3
import os

class DataMigration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for command in self.get_commands():
            command.cog_category = "Moderation"

    @commands.command(name="restoredata", help="Migrate level_data.json to the SQLite database.")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def migrate_levels(self, ctx):
        if ctx.author.id != 1194815627324571668:
            return
        json_path = "data/level_data.json"
        db_path = "data/botdata.db"
        guild = ctx.guild

        if not os.path.exists(json_path):
            await ctx.send("❌ JSON file not found.")
            return

        try:
            with open(json_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            await ctx.send("❌ Failed to parse JSON file.")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            migrated_count = 0
            skipped_count = 0

            for user_id, stats in data.items():
                member = guild.get_member(int(user_id))
                if not member:
                    skipped_count += 1
                    continue  # Skip if user is not in the server

                total_messages = stats.get("total_messages", 0)
                replies_received = stats.get("replies_received", 0)
                total_attachments = stats.get("total_attachments", 0)
                balance = stats.get("balance", 0)

                cursor.execute("""
                    INSERT INTO userstats (
                        user_id,
                        guild_id,
                        balance,
                        level,
                        xp,
                        main_channel_messages,
                        total_messages,
                        replies_received,
                        total_attachments,
                        vc_time,
                        reputation,
                        milestone
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, guild_id) DO UPDATE SET
                        balance = excluded.balance,
                        total_messages = excluded.total_messages,
                        replies_received = excluded.replies_received,
                        total_attachments = excluded.total_attachments
                """, (
                    user_id,
                    str(guild.id),
                    balance,
                    0,  # level
                    0,  # xp
                    0,  # main_channel_messages
                    total_messages,
                    replies_received,
                    total_attachments,
                    0,  # vc_time
                    0,  # reputation
                    0   # milestone
                ))

                migrated_count += 1

            conn.commit()
            await ctx.send(f"✅ Migration completed: {migrated_count} users added/updated. {skipped_count} skipped (not in server).")
        except Exception as e:
            await ctx.send(f"❌ Migration failed: {e}")
        finally:
            conn.close()

# Required setup function for the bot to load this cog
async def setup(bot):
    await bot.add_cog(DataMigration(bot))
