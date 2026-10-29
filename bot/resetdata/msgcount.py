import discord
from database.connect import get_connection
from utils import bot_instance

bot = bot_instance.instance

async def reset_messages(field: str):
    print("🔁 Resetting message counts...")

    try:
        conn = get_connection()
        c = conn.cursor()

        if field == "daily-all":
            c.execute("""
            UPDATE messages SET
                daily_messages = 0, daily_main_channel_messages = 0
                """)
        elif field == "weekly-all":
            c.execute("""
            UPDATE messages SET
                daily_messages = 0, weekly_messages = 0, daily_main_channel_messages = 0, weekly_main_channel_messages = 0
        """)
        elif field == "monthly-all":
            c.execute("""
            UPDATE messages SET
                daily_messages = 0, weekly_messages = 0, monthly_messages = 0,
                daily_main_channel_messages = 0, weekly_main_channel_messages = 0, monthly_main_channel_messages = 0
        """)
        
        conn.commit()
    except Exception as e:
        print(f"An error occured while resetting message count: {e}")
    finally:
        conn.close()

async def reset_user_messages(field: str , user_id: str, guild_id: str):
    try:
        conn = get_connection()
        c = conn.cursor()

        if field == "daily-one":
            c.execute("""
            UPDATE messages SET
                daily_messages = 0, daily_main_channel_messages = 0
            WHERE user_id = ? AND guild_id = ? 
                """, (user_id, guild_id))
        elif field == "weekly-one":
            c.execute("""
            UPDATE messages SET
                daily_messages = 0, weekly_messages = 0, daily_main_channel_messages = 0, weekly_main_channel_messages = 0
            WHERE user_id = ? AND guild_id = ?
        """, (user_id, guild_id))
        elif field == "monthly-one":
            c.execute("""
            UPDATE messages SET
                daily_messages = 0, weekly_messages = 0, monthly_messages = 0,
                daily_main_channel_messages = 0, weekly_main_channel_messages = 0, monthly_main_channel_messages = 0
            WHERE user_id = ? AND guild_id = ?
        """, (user_id, guild_id))
        
        conn.commit()
    except Exception as e:
        print(f"An error occured while resetting message count: {e}")
    finally:
        conn.close()
    
async def reset_all_users_messages(field: str , guild_id: str):
    try:
        conn = get_connection()
        c = conn.cursor()

        if field == "daily-all":
            c.execute("""
            UPDATE messages SET
                daily_messages = 0, daily_main_channel_messages = 0
            WHERE guild_id = ? 
                """, (guild_id,))
        elif field == "weekly-all":
            c.execute("""
            UPDATE messages SET
                daily_messages = 0, weekly_messages = 0, daily_main_channel_messages = 0, weekly_main_channel_messages = 0
            WHERE guild_id = ?
        """, (guild_id,))
        elif field == "monthly-all":
            c.execute("""
            UPDATE messages SET
                daily_messages = 0, weekly_messages = 0, monthly_messages = 0,
                daily_main_channel_messages = 0, weekly_main_channel_messages = 0, monthly_main_channel_messages = 0
            WHERE guild_id = ?
        """, (guild_id,))
        
        conn.commit()
    except Exception as e:
        print(f"An error occured while resetting message count: {e}")
    finally:
        conn.close()