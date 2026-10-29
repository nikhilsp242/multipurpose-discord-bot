from database.connect import get_connection

class Birthdays:
    def __init__(self, user_id, guild_id, day = 0, month = 0, year = 0, timezone = "Asia/Kolkata"):
        self.user_id = user_id
        self.guild_id = guild_id
        self.day = day
        self.month = month
        self.year = year
        self.timezone = timezone

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get_one(cls, user_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM birthday
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            row = c.fetchone()
            return cls.from_db_row(row) if row else cls(user_id, guild_id)
        except Exception as e:
            print(f"An error occurred while fetching birthday data : {e}")
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def get_all(cls, day, month, timezone):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM birthday
                WHERE day = ? AND month = ? AND timezone = ?      
            """, (day, month, timezone))
            rows = c.fetchall()
            return [cls.from_db_row(row) for row in rows] if rows else None
        except Exception as e:
            print(f"An error occurred while fetching birthday data : {e}")
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def get_guild_bdays(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM birthday
                WHERE guild_id = ?
                ORDER BY month, day     
            """, (guild_id,))
            rows = c.fetchall()
            return [cls.from_db_row(row) for row in rows] if rows else None
        except Exception as e:
            print(f"An error occurred while fetching birthday data for guild : {e}")
        finally:
            if conn:
                conn.close()

        
    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
            INSERT INTO birthday (user_id, guild_id, day, month, year, timezone)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, guild_id) DO UPDATE SET
                day = excluded.day,
                month = excluded.month,
                year = excluded.year,
                timezone = excluded.timezone
            """, (self.user_id, self.guild_id, self.day, self.month, self.year, self.timezone))
            conn.commit()
        except Exception as e:
            print(f"An error occurred while saving birthday data : {e}")
        finally:
            if conn:
                conn.close()
    
    def delete(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM birthday WHERE user_id = ? AND guild_id = ?", (self.user_id, self.guild_id))
            conn.commit()
        except Exception as e:
            print(f"Error deleting birthday of user {self.user_id} in guild {self.guild_id}: {e}")
        finally:
            conn.close()
                
            
