from database.connect import get_connection

class Channel:
    def __init__(self, channel_id, guild_id, name="Uninitalized", is_main_channel=False, is_media_channel=False, is_coin_channel=False, is_xp_channel=False, is_bday_channel=False):
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.name = name
        self.is_main_channel = is_main_channel
        self.is_media_channel = is_media_channel
        self.is_coin_channel = is_coin_channel
        self.is_xp_channel = is_xp_channel
        self.is_bday_channel = is_bday_channel

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

    @classmethod
    def get(cls, channel_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT *
                FROM channels
                WHERE channel_id = ? AND guild_id = ?
            """, (channel_id, guild_id))
            row = c.fetchone()            
            if row:
                return cls.from_db_row(row)
            else:
                return cls(channel_id=channel_id, guild_id=guild_id)
        except Exception as e:
            print(f"Error fetching channel {channel_id} in guild {guild_id}: {e}")
        finally:
            conn.close()
    
    @classmethod
    def get_channel(cls, guild_id, channelType):
        try:
            conn = get_connection()
            c = conn.cursor()
            query = f"""
                SELECT *
                FROM channels
                WHERE guild_id = ? AND {channelType} = TRUE
            """
            c.execute(query,(guild_id,))
            row = c.fetchone()
            return cls.from_db_row(row) if row else None
        except Exception as e:
            print(f"An error occurred while fetching {channelType} : {e}")
        finally:
            if conn:
                conn.close()

    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO channels (channel_id, guild_id, name, isMainChannel, isMediaChannel, isCoinChannel, isXPChannel, isBdayChannel)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(channel_id, guild_id) DO UPDATE SET
                    name = excluded.name,
                    isMainChannel = excluded.isMainChannel,
                    isMediaChannel = excluded.isMediaChannel,
                    isCoinChannel = excluded.isCoinChannel,
                    isXPChannel = excluded.isXPChannel,
                    isBdayChannel = excluded.isBdayChannel
            """, (self.channel_id, self.guild_id, self.name, self.is_main_channel, self.is_media_channel, self.is_coin_channel, self.is_xp_channel, self.is_bday_channel))
            conn.commit()
        except Exception as e:
            print(f"Error saving channel {self.channel_id} in guild {self.guild_id}: {e}")
        finally:
            conn.close()
    
    def delete(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM channels WHERE channel_id = ? AND guild_id = ?", (self.channel_id, self.guild_id))
            conn.commit()
        except Exception as e:
            print(f"Error deleting channel {self.channel_id} in guild {self.guild_id}: {e}")
        finally:
            conn.close()
