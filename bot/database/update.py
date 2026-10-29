from database.connect import get_connection

def create_table():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS conversation_memory (
            channel_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        print("✅ Table created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()


def delete_table():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS invitetracking")
        conn.commit()
        print("✅ Tables deleted successfully.")
    except Exception as e:
        print(f"Error adding new columns: {e}")
    finally:
        conn.close() 

def add_columns():
    try:
        conn = get_connection()
        c = conn.cursor()
        # c.execute("ALTER TABLE channels ADD COLUMN isBdayChannel BOOLEAN DEFAULT FALSE")
        c.execute("ALTER TABLE memberinout ADD COLUMN welcome_role TEXT")
        # c.execute("DROP TABLE IF EXISTS roles")
        conn.commit()
        print("✅ New columns added successfully.")
    except Exception as e:
        print(f"Error adding new columns: {e}")
    finally:
        conn.close()

def delete_row():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM roles WHERE role_id = 1212723413886570496 AND guild_id = 1183064183646982164")
        conn.commit()
        print("✅ Deleted a row successfully.")
    except Exception as e:
        print(f"Error deleting a row: {e}")
    finally:
        conn.close()
    
