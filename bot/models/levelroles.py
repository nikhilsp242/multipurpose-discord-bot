from database.connect import get_connection

class LevelRole:
    def __init__(self, guild_id, role_id = None, level = 0, xp_required = None, level_perks = None):
        self.guild_id = guild_id
        self.role_id = role_id
        self.level = level
        self.xp_required = xp_required
        self.level_perks = level_perks

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

    @classmethod
    def get(cls, guild_id, xp_required):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT *
                FROM levelroles
                WHERE guild_id = ? AND xpRequired <= ?
                ORDER BY level DESC
                LIMIT 1
            """, (guild_id, xp_required))
            row = c.fetchone()
            if row:
                return cls.from_db_row(row)
            else:
                return cls(guild_id, xp_required)
        except Exception as e:
            print(f"Error fetching level role for guild {guild_id} with xp_required {xp_required}: {e}")
        finally:
            conn.close()

    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO levelroles (guild_id, role_id, level, xpRequired, level_perks)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(guild_id, role_id) DO UPDATE SET
                    level = excluded.level,
                    xpRequired = excluded.xpRequired,
                    level_perks = excluded.level_perks
            """, (self.guild_id, self.role_id, self.level, self.xp_required, self.level_perks))
            conn.commit()
        except Exception as e:
            print(f"Error saving level role for guild {self.guild_id} with role {self.role_id}: {e}")
        finally:
            conn.close()
    
    @classmethod
    def delete_by_level(cls, guild_id, level):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                DELETE FROM levelroles
                WHERE guild_id = ? AND level = ?
            """, (guild_id, level))
            conn.commit()
            print(f"✅ Level role at level {level} deleted for guild {guild_id}")
        except Exception as e:
            print(f"Error deleting level role for guild {guild_id} at level {level}: {e}")
        finally:
            conn.close()