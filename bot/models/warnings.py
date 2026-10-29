from database.connect import get_connection

class Warnings:
    def __init__(self, user_id, guild_id, warns=0, prev_warn=None):
        self.user_id = user_id
        self.guild_id = guild_id
        self.warns = warns
        self.prev_warn = prev_warn
    
    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get(cls, user_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM warnings
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            row = c.fetchone()
            return cls.from_db_row(row) if row else cls(user_id, guild_id)
        except Exception as e:
            print(f"An error occurred while getting warnings : {e}")
        finally:
            if conn:
                conn.close()
    

    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO warnings (user_id, guild_id, warns, prev_warn)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (user_id, guild_id) DO UPDATE SET
                    warns = excluded.warns,
                    prev_warn = excluded.prev_warn
                """, (self.user_id, self.guild_id, self.warns, self.prev_warn))
            conn.commit()
        except Exception as e:
            print(f"An error occurred while saving warnings : {e}")
        finally:
            if conn:
                conn.close()