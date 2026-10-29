from database.connect import get_connection 

class MessageLogger:
    def __init__(self, guild_id, message_logging_enabled=False, humanlog_channel=None, botlog_channel=None):
        self.guild_id = guild_id
        self.message_logging_enabled = message_logging_enabled
        self.humanlog_channel = humanlog_channel
        self.botlog_channel = botlog_channel

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

    @classmethod
    def get(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT * FROM messagelogging WHERE guild_id = ?
            """, (guild_id,))
            row = c.fetchone()
            return cls.from_db_row(row) if row else cls(guild_id)
        except Exception as e:
            print(f"[MessageLogging] Error fetching settings for guild {guild_id}: {e}")
            return cls(guild_id)
        finally:
            conn.close()

    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO messagelogging (guild_id, message_logging_enabled, humanlog_channel, botlog_channel)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    message_logging_enabled = excluded.message_logging_enabled,
                    humanlog_channel = excluded.humanlog_channel,
                    botlog_channel = excluded.botlog_channel
            """, (self.guild_id, self.message_logging_enabled, self.humanlog_channel, self.botlog_channel))
            conn.commit()
        except Exception as e:
            print(f"[MessageLogging] Error saving settings for guild {self.guild_id}: {e}")
        finally:
            conn.close()
