from database.connect import get_connection

class InviteTrack:
    def __init__(self, guild_id, invite_tracking_enabled=False, invitelog_channel=None):
        self.guild_id = guild_id
        self.invite_tracking_enabled = invite_tracking_enabled
        self.invitelog_channel = invitelog_channel
    
    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM invitetracking
                WHERE guild_id = ?
            """,(guild_id,))
            row = c.fetchone()
            return cls.from_db_row(row) if row else cls(guild_id)
        except Exception as e:
            print(f"An error occured while getting invitetracking data : {e}")
        finally:
            if conn:
                conn.close()

    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO invitetracking (guild_id, invite_tracking_enabled, invitelog_channel)
                VALUES (?, ?, ?)
                ON CONFLICT (guild_id) DO UPDATE SET
                    invite_tracking_enabled = excluded.invite_tracking_enabled,
                    invitelog_channel = excluded.invitelog_channel
                """, (self.guild_id, self.invite_tracking_enabled, self.invitelog_channel))
            conn.commit()
        except Exception as e:
            print(f"An error occurred while saving invitetracking data : {e}")
        finally:
            if conn:
                conn.close() 