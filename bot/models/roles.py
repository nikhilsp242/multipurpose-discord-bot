from database.connect import get_connection

class Roles:
    def __init__(self, guild_id, role_id=None, role_name="Uninitialized", is_bday_role = False):
        self.guild_id = guild_id
        self.role_id = role_id
        self.role_name = role_name
        self.is_bday_role = is_bday_role
    
    @classmethod
    def from_db_row(cls, row):
        return cls(*row)
    
    @classmethod
    def get_role_to_save(cls, guild_id):
        return cls(guild_id)

    @classmethod
    def get_role_to_edit(cls, guild_id, role_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            query = f"""
                SELECT * FROM roles
                WHERE guild_id = ? AND role_id = ?
            """
            c.execute(query, (guild_id, role_id))
            row = c.fetchone()
            return cls.from_db_row(row) if row else None
        except Exception as e:
            print(f"An error occurred while fetching role {role_id} : {e}")
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_role(cls, guild_id, roleType):
        try:
            conn = get_connection()
            c = conn.cursor()
            query = f"""
                SELECT * FROM roles
                WHERE guild_id = ? AND {roleType} = TRUE
            """
            c.execute(query, (guild_id,))
            row = c.fetchone()
            return cls.from_db_row(row) if row else None
        except Exception as e:
            print(f"An error occurred while fetching role {roleType} : {e}")
        finally:
            if conn:
                conn.close()
    
    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO roles (guild_id, role_id, role_name, is_bday_role)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (guild_id, role_id) DO UPDATE SET
                    role_name = excluded.role_name,
                    is_bday_role = excluded.is_bday_role
                """, (self.guild_id, self.role_id, self.role_name, self.is_bday_role))
            conn.commit()
        except Exception as e:
            print(f"An error occurred while saving role data : {e}")
        finally:
            if conn:
                conn.close()