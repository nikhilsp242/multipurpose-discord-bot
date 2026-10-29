from database.connect import get_connection

class ArchivedChannel:
    def __init__(self, channel_id: str, guild_id: str, category_id: str = None):
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.category_id = category_id

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

    @classmethod
    def get(cls, channel_id: str, guild_id: str):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT *
                FROM archived_channels
                WHERE channel_id = ? AND guild_id = ?
            """, (channel_id, guild_id))
            row = c.fetchone()
            return cls.from_db_row(row) if row else None
        except Exception as e:
            print(f"[ArchivedChannel] Error fetching archived channel {channel_id} in guild {guild_id}: {e}")
        finally:
            conn.close()

    # @classmethod
    # def get_all_in_guild(cls, guild_id: str):
    #     try:
    #         conn = get_connection()
    #         c = conn.cursor()
    #         c.execute("""
    #             SELECT channel_id, guild_id, category_id
    #             FROM archived_channels
    #             WHERE guild_id = ?
    #         """, (guild_id,))
    #         rows = c.fetchall()
    #         return [cls.from_db_row(row) for row in rows] if rows else []
    #     except Exception as e:
    #         print(f"[ArchivedChannel] Error fetching archived channels in guild {guild_id}: {e}")
    #     finally:
    #         conn.close()

    @staticmethod
    def save(channel_id, guild_id, category_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO archived_channels (channel_id, guild_id, category_id)
                VALUES (?, ?, ?)
                ON CONFLICT(channel_id, guild_id) DO UPDATE SET
                    category_id = excluded.category_id
            """, (channel_id, guild_id, category_id))
            conn.commit()
        except Exception as e:
            print(f"[ArchivedChannel] Error saving archived channel {channel_id} in guild {guild_id}: {e}")
        finally:
            conn.close()

    def delete(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                DELETE FROM archived_channels
                WHERE channel_id = ? AND guild_id = ?
            """, (self.channel_id, self.guild_id))
            conn.commit()
        except Exception as e:
            print(f"[ArchivedChannel] Error deleting archived channel {self.channel_id} in guild {self.guild_id}: {e}")
        finally:
            conn.close()
