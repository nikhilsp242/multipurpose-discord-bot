from database.connect import get_connection

def modify_column(table_name, guild_id, column_name, value):
    try:
        conn = get_connection()
        c = conn.cursor()
        query = f"""
            UPDATE {table_name}
            SET {column_name} = ?
            WHERE guild_id = ?
            """
        c.execute(query, (value, guild_id))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while upating table {table_name} : {e}")
    finally:
        conn.close()
