from database.connect import get_connection

def mainChannelAvailable(guild_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT channel_id
            FROM channels
            WHERE guild_id = ? AND isMainChannel = TRUE
        """, (guild_id,))
        row = c.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Error fetching main channel in guild {guild_id}: {e}")
    finally:
        conn.close()

def bdayChannelAvailable(guild_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT channel_id
            FROM channels
            WHERE guild_id = ? AND isBdayChannel = TRUE
        """, (guild_id,))
        row = c.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Error fetching bday channel in guild {guild_id}: {e}")
    finally:
        conn.close()

def bdayRoleAvailable(guild_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT role_id
            FROM roles
            WHERE guild_id = ? AND is_bday_role = TRUE
            """, (guild_id,))
        row = c.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Error fetching birthday role in guild {guild_id}: {e}")
    finally:
        if conn:
            conn.close()