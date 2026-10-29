from database.connect import get_connection

class WarnSettings:
    def __init__(self, guild_id, channel_id=None, channel_name=None):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.channel_name = channel_name

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM warn_setup
                WHERE guild_id = ?
                """, (guild_id,))
            row = c.fetchone()
            return cls.from_db_row(row) if row else cls(guild_id)
        except Exception as e:
            print(f"An error occurred while getting warn_setup : {e}")
        finally:
            if conn:
                conn.close()
    
    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO warn_setup (guild_id, channel_id, channel_name)
                VALUES (?, ?, ?)
                ON CONFLICT (guild_id) DO UPDATE SET
                    channel_id = excluded.channel_id,
                    channel_name = excluded.channel_name
                """, (self.guild_id, self.channel_id, self.channel_name))
            conn.commit()
        except Exception as e:
            print(f"An error occured while saving warn_setup : {e}")
        finally:
            if conn:
                conn.close()