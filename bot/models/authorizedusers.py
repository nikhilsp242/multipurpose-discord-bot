from database.connect import get_connection

class AuthorizedUsers:
    def __init__(self, user_id, guild_id):
        self.user_id = user_id
        self.guild_id = guild_id

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get_one(cls, user_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM authorized_users
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            row = c.fetchone()
            return cls.from_db_row(row) if row else None
        except Exception as e:
            print(f"An error occurred while fetching authorized user : {e}")
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def get_all(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM authorized_users
                WHERE guild_id = ?
            """, (guild_id,))
            rows = c.fetchall()
            return [cls.from_db_row(row) for row in rows] if rows else None
        except Exception as e:
            print(f"An error occurred while fetching authorized user : {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def save(user_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO authorized_users (user_id, guild_id)
                VALUES (?, ?)
                ON CONFLICT(user_id, guild_id) DO NOTHING
            """, (user_id, guild_id))
            conn.commit()
        except Exception as e:
            print(f"An error occured while saving authorized users : {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def remove(user_id: str, guild_id: str):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                DELETE FROM authorized_users
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            conn.commit()
        except Exception as e:
            print(f"Error removing authorized user {user_id} in guild {guild_id}: {e}")
        finally:
            conn.close()