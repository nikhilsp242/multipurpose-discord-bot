from database.connect import get_connection

class GuildActionCmds:
    def __init__(self, guild_id, rating=None, role_id=None, role_name=None):
        self.guild_id = guild_id
        self.rating = rating
        self.role_id = role_id
        self.role_name = role_name
    
    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT *
                FROM actioncmds
                WHERE guild_id = ?
            """, (guild_id,))
            row = c.fetchone()
            return cls.from_db_row(row) if row else cls(guild_id)
        except Exception as e:
            print(f"[ActionCmds] Error fetching data for guild {guild_id}: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def save(guild_id, rating=None, role_id=None, role_name=None):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO actioncmds (guild_id, rating, role_id, role_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    rating = excluded.rating,
                    role_id = excluded.role_id,
                    role_name = excluded.role_name
            """, (guild_id, rating, role_id, role_name))
            conn.commit()
        except Exception as e:
            print(f"[ActionCmds] Error saving data for guild {guild_id}: {e}")
        finally:
            conn.close()
