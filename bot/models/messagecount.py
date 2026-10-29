from database.connect import get_connection

class MessageCount:
    def __init__(self, user_id, guild_id, daily_messages=0, weekly_messages=0, monthly_messages=0,
                 daily_main_channel_messages=0, weekly_main_channel_messages=0, monthly_main_channel_messages=0):
        self.user_id = user_id
        self.guild_id = guild_id
        self.daily_messages = daily_messages
        self.weekly_messages = weekly_messages
        self.monthly_messages = monthly_messages
        self.daily_main_channel_messages = daily_main_channel_messages
        self.weekly_main_channel_messages = weekly_main_channel_messages
        self.monthly_main_channel_messages = monthly_main_channel_messages

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

    @classmethod
    def get_one(cls, user_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT *
                FROM messages
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            row = c.fetchone()
            if row:
                return cls.from_db_row(row)
            else:
                return cls(user_id=user_id, guild_id=guild_id)
        except Exception as e:    
            print(f"Error fetching message count for user {user_id} in guild {guild_id}: {e}")
        finally:
            conn.close()

    @classmethod
    def get_all(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT *
                FROM messages
                WHERE guild_id = ?
            """, (guild_id,))
            rows = c.fetchall()
            return [cls.from_db_row(row) for row in rows] if rows else []
        except Exception as e:
            print(f"Error fetching all message counts for guild {guild_id}: {e}")
        finally:
            conn.close() 

    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO messages (user_id, guild_id, daily_messages, weekly_messages, monthly_messages,
                                                daily_main_channel_messages, weekly_main_channel_messages,
                                                monthly_main_channel_messages)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, guild_id) DO UPDATE SET
                    daily_messages = excluded.daily_messages,
                    weekly_messages = excluded.weekly_messages,
                    monthly_messages = excluded.monthly_messages,
                    daily_main_channel_messages = excluded.daily_main_channel_messages,
                    weekly_main_channel_messages = excluded.weekly_main_channel_messages,
                    monthly_main_channel_messages = excluded.monthly_main_channel_messages
            """, (self.user_id, self.guild_id, self.daily_messages, self.weekly_messages, self.monthly_messages,
                self.daily_main_channel_messages, self.weekly_main_channel_messages, self.monthly_main_channel_messages))
            conn.commit()
        except Exception as e:
            print(f"Error saving message count for user {self.user_id} in guild {self.guild_id}: {e}")
        finally:
            conn.close()