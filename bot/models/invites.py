from database.connect import get_connection

class Invites:
    def __init__(self, guild_id, invite_id=None, inviter_id=None, uses=None):
        self.guild_id = guild_id
        self.invite_id = invite_id
        self.inviter_id = inviter_id
        self.uses = uses
    
    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get_one(cls, guild_id, invite_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM invites
                WHERE guild_id = ? AND invite_id = ?
            """, (guild_id, invite_id))
            row = c.fetchone()
            return cls.from_db_row(row) if row else None
        except Exception as e:
            print(f"An error occurred while getting invites : {e}")
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def get_all(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM invites
                WHERE guild_id = ?
            """, (guild_id,))
            rows = c.fetchall()
            return [cls.from_db_row(row) for row in rows] if rows else None
        except Exception as e:
            print(f"An error occurred while getting invites : {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def save(guild_id, invite_code, inviter_id, uses):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO invites (guild_id, invite_id, inviter_id, uses)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id, invite_id) DO UPDATE SET
                    inviter_id = excluded.inviter_id,
                    uses = excluded.uses
            """, (guild_id, invite_code, inviter_id, uses))
            conn.commit()
        except Exception as e:
            print(f"An error occured while saving invites : {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def delete(guild_id, invite_code):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                DELETE FROM invites
                WHERE guild_id = ? AND invite_id = ?
            """, (guild_id, invite_code))
            conn.commit()
        except Exception as e:
            print(f"Error deleting invite {invite_code} from guild {guild_id}: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def delete_all(guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                DELETE FROM invites
                WHERE guild_id = ?
            """, (guild_id,))
            conn.commit()
        except Exception as e:
            print(f"Error deleting invites from guild {guild_id}: {e}")
        finally:
            conn.close()

    @staticmethod
    def clear():
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM invites")
            conn.commit()
            c.execute("VACUUM")  # Reclaims unused space
            conn.commit()
        except Exception as e:
            print(f"Error clearing all invites: {e}")
        finally:
            conn.close()
        
    