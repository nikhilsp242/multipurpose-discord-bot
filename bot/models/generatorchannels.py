from database.connect import get_connection

class GeneratorChannels:
    def __init__(self, channel_id, guild_id, channel_name="Uninitialized"):
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.channel_name = channel_name
    
    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get_to_save(cls, channel_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM generator_channels
                WHERE channel_id = ? AND guild_id = ?
            """, (channel_id, guild_id))
            row = c.fetchone()
            return cls.from_db_row(row) if row else cls(channel_id, guild_id)
        except Exception as e:
            print(f"An error occurred while fetching generator channel : {e}")
        finally:
            if conn:
                conn.close()

    @classmethod
    def get(cls, channel_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM generator_channels
                WHERE channel_id = ? AND guild_id = ?
            """, (channel_id, guild_id))
            row = c.fetchone()
            return cls.from_db_row(row) if row else None
        except Exception as e:
            print(f"An error occurred while fetching generator channel : {e}")
        finally:
            if conn:
                conn.close()
    
    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO generator_channels (channel_id , guild_id, channel_name)
                VALUES (?, ?, ?)
                ON CONFLICT (channel_id, guild_id) DO UPDATE SET
                    channel_name = excluded.channel_name
                """, (self.channel_id, self.guild_id, self.channel_name))
            conn.commit()
        except Exception as e:
            print(f"An error occurred while saving generator channels : {e}")
        finally:
            if conn:
                conn.close()
    
