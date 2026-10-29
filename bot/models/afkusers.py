import time
from database.connect import get_connection

class AfkUsers:
    def __init__(self, user_id, guild_id, reason=None, since_timestamp=None):
        self.user_id = user_id
        self.guild_id = guild_id
        self.reason = reason
        self.since_timestamp = since_timestamp or time.time()

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

    @classmethod
    def get(cls, user_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT user_id, guild_id, reason, since_timestamp
                FROM afk
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            row = c.fetchone()
            return cls.from_db_row(row) if row else None
        except Exception as e:
            print(f"[AFK] Error fetching AFK for user {user_id} in guild {guild_id}: {e}")
        finally:
            conn.close()

    @classmethod
    def get_all_afk_in_guild(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT user_id, guild_id, reason, since_timestamp
                FROM afk
                WHERE guild_id = ?
            """, (guild_id,))
            rows = c.fetchall()
            return [cls.from_db_row(row) for row in rows] if rows else []
        except Exception as e:
            print(f"[AFK] Error fetching AFK list for guild {guild_id}: {e}")
        finally:
            conn.close()

    @staticmethod
    def save(user_id, guild_id, reason, since_timestamp):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO afk (user_id, guild_id, reason, since_timestamp)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, guild_id) DO UPDATE SET
                    reason = excluded.reason,
                    since_timestamp = excluded.since_timestamp
            """, (user_id, guild_id, reason, since_timestamp))
            conn.commit()
        except Exception as e:
            print(f"[AFK] Error saving AFK for user {user_id} in guild {guild_id}: {e}")
        finally:
            conn.close()

    def delete(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                DELETE FROM afk
                WHERE user_id = ? AND guild_id = ?
            """, (self.user_id, self.guild_id))
            conn.commit()
        except Exception as e:
            print(f"[AFK] Error deleting AFK for user {self.user_id} in guild {self.guild_id}: {e}")
        finally:
            conn.close()