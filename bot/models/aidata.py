from database.connect import get_connection
from typing import List, Optional
from datetime import datetime, timezone

class AIData:
    def __init__(self, channel_id: str, user_id: str, role: str, content: str, timestamp: Optional[str] = None):
        self.channel_id = channel_id
        self.user_id = user_id
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

    @classmethod
    def get(cls, channel_id: str, user_id: str) -> List["AIData"]:
        """
        Fetch conversation history for a user in a channel, ordered by timestamp.
        """
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "SELECT channel_id, user_id, role, content, timestamp FROM conversation_memory WHERE channel_id = ? AND user_id = ? ORDER BY timestamp ASC",
                (channel_id, user_id)
            )
            rows = c.fetchall()
            return [cls.from_db_row(row) for row in rows] if rows else []
        except Exception as e:
            print(f"[AIData.get] Error: {e}")
            return []
        finally:
            conn.close()

    def save(self):
        """
        Save the current message entry to the database.
        """
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO conversation_memory (channel_id, user_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (self.channel_id, self.user_id, self.role, self.content, self.timestamp)
            )
            conn.commit()
        except Exception as e:
            print(f"[AIData.save] Error: {e}")
        finally:
            conn.close()

    @classmethod
    def delete_old(cls, minutes: int = 5):
        """
        Optionally clear out old data beyond X minutes for cleanup if desired.
        """
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "DELETE FROM conversation_memory WHERE timestamp <= datetime('now', ?)",
                (f'-{minutes} minutes',)
            )
            conn.commit()
        except Exception as e:
            print(f"[AIData.delete_old] Error: {e}")
        finally:
            conn.close()
    
    @classmethod
    def delete(cls, channel_id, user_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            if user_id:
                c.execute(
                    "DELETE FROM conversation_memory WHERE channel_id = ? AND user_id = ?",
                    (channel_id, user_id)
                )
            else:
                c.execute(
                    "DELETE FROM conversation_memory WHERE channel_id = ?",
                    (channel_id,)
                )
            conn.commit()
        except Exception as e:
            print(f"⚠️ Failed to clear memory from the database: `{e}`")
        finally:
            conn.close()