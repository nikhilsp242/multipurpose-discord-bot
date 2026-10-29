from database.connect import get_connection

class UserStats:
    def __init__(self, user_id, guild_id, balance=0, level=0, xp=0, main_channel_messages=0, total_messages=0, replies_received=0, total_attachments=0, vc_time = 0, reputation=0, milestone = 0):
        self.user_id = user_id
        self.guild_id = guild_id
        self.balance = balance
        self.level = level
        self.xp = xp
        self.main_channel_messages = main_channel_messages
        self.total_messages = total_messages
        self.replies_received = replies_received
        self.total_attachments = total_attachments
        self.vc_time = vc_time
        self.reputation = reputation
        self.milestone = milestone

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get_one(cls, user_id, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT *
                FROM userstats
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            row = c.fetchone()
            if row:
                return cls.from_db_row(row)
            else:
                return cls(user_id=user_id, guild_id=guild_id)
        except Exception as e:
            print(f"Error fetching user stats for user {user_id} in guild {guild_id}: {e}")
        finally:
            conn.close()
        
    @classmethod
    def get_all(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT *
                FROM userstats
                WHERE guild_id = ?
            """, (guild_id,))
            rows = c.fetchall()
            return [cls.from_db_row(row) for row in rows] if rows else []
        except Exception as e:
            print(f"Error fetching all user stats for guild {guild_id}: {e}")
        finally:
            conn.close()
    

    @staticmethod
    def update_field(user_id, guild_id, field, amount=1):
        ALLOWED_FIELDS = {"xp", "balance", "replies_received", "total_messages", "vc_time", "total_attachments"}
        if field not in ALLOWED_FIELDS:
            raise ValueError(f'Invalid field name : {field}')
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute(f"""
                UPDATE userstats
                SET {field} = {field} + ?
                WHERE user_id = ? AND guild_id = ?
            """, (amount, user_id, guild_id))
            conn.commit()
        except Exception as e:
            print(f"Error fetching all user stats for guild {guild_id}: {e}")
        finally:
            conn.close()

        
    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO userstats (user_id, guild_id, balance, level, xp, main_channel_messages, total_messages, replies_received, total_attachments, vc_time, reputation, milestone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, guild_id) DO UPDATE SET
                balance = excluded.balance,
                level = excluded.level, 
                xp = excluded.xp,
                main_channel_messages = excluded.main_channel_messages,
                total_messages = excluded.total_messages, 
                replies_received = excluded.replies_received,
                total_attachments = excluded.total_attachments,
                vc_time = excluded.vc_time,
                reputation = excluded.reputation,
                milestone = excluded.milestone      
            """, (self.user_id, self.guild_id, self.balance, self.level, self.xp, self.main_channel_messages, self.total_messages, self.replies_received, self.total_attachments, self.vc_time, self.reputation, self.milestone))
            conn.commit()
        except Exception as e:
            print(f"Error saving user stats for user {self.user_id} in guild {self.guild_id}: {e}")
        finally:
            conn.close()
        
    