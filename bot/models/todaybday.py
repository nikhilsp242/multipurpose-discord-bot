from database.connect import get_connection

class TodayBirthdays:
    def __init__(self, user_id, guild_id, role_id=None, time_stamp=None):
        self.user_id = user_id
        self.guild_id = guild_id
        self.role_id = role_id
        self.time_stamp = time_stamp

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get_one(cls, user_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM birthday_users
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            row = c.fetchone()
            return cls.from_db_row(row) if row else cls(user_id, guild_id)
        except Exception as e:
            print(f"An error occurred while fetching today's birthday : {e}")
        finally:
            if conn:
                conn.close()
        
    @classmethod
    def get_all(cls):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM birthday_users
            """)
            rows = c.fetchall()
            return [cls.from_db_row(row) for row in rows] if rows else None
        except Exception as e:
            print(f"An error occurred while fetching today's birthday : {e}")
        finally:
            if conn:
                conn.close()
    
    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO birthday_users (user_id, guild_id, role_id, time_stamp)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (user_id, guild_id) DO UPDATE SET
                    role_id = excluded.role_id,
                    time_stamp = excluded.time_stamp
                """, (self.user_id, self.guild_id, self.role_id, self.time_stamp))
            conn.commit()
        except Exception as e:
            print(f"An error occurred while saving today birthday users : {e}")
        finally:
            if conn:
                conn.close()
    
    def delete(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM birthday_users WHERE user_id = ? AND guild_id = ?", (self.user_id, self.guild_id))
            conn.commit()
        except Exception as e:
            print(f"Error deleting today birthday user {self.user_id} in guild {self.guild_id}: {e}")
        finally:
            conn.close()