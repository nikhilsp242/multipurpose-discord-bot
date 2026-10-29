from database.connect import get_connection

def setup_tables():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS userstats (
            user_id TEXT NOT NULL,
            guild_id TEXT DEFAULT NULL,  
            balance INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            main_channel_messages INTEGER DEFAULT 0,
            total_messages INTEGER DEFAULT 0,
            replies_received INTEGER DEFAULT 0,
            total_attachments INTEGER DEFAULT 0,
            vc_time INTEGER DEFAULT 0,
            reputation INTEGER DEFAULT 0,
            milestone INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            user_id TEXT NOT NULL,
            guild_id TEXT DEFAULT NULL,
            daily_messages INTEGER DEFAULT 0,
            weekly_messages INTEGER DEFAULT 0,
            monthly_messages INTEGER DEFAULT 0,
            daily_main_channel_messages INTEGER DEFAULT 0,
            weekly_main_channel_messages INTEGER DEFAULT 0,
            monthly_main_channel_messages INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            channel_id TEXT NOT NULL,
            guild_id TEXT DEFAULT NULL,
            name TEXT NOT NULL,
            isMainChannel BOOLEAN DEFAULT FALSE,
            isMediaChannel BOOLEAN DEFAULT FALSE,
            isCoinChannel BOOLEAN DEFAULT FALSE,
            isXPChannel BOOLEAN DEFAULT FALSE,
            isBdayChannel BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (channel_id, guild_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS levelroles (
            guild_id TEXT NOT NULL,
            role_id TEXT NOT NULL,
            level INTEGER NOT NULL,
            xpRequired INTEGER NOT NULL,
            level_perks TEXT DEFAULT NULL,
            PRIMARY KEY (guild_id, role_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS levelup_settings (
            guild_id TEXT PRIMARY KEY,
            booster_coin_multiplier INTEGER DEFAULT 1,
            booster_xp_multiplier INTEGER DEFAULT 1,
            levelup_enabled BOOLEAN DEFAULT FALSE,
            vc_levelup_enabled BOOLEAN DEFAULT FALSE,
            levelup_channel TEXT DEFAULT NULL,
            enable_xp_for_all_channels BOOLEAN DEFAULT TRUE,
            enable_coins_for_all_channels BOOLEAN DEFAULT TRUE,
            custom_levelup_system BOOLEAN DEFAULT FALSE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS messagelogging (
            guild_id TEXT PRIMARY KEY,
            message_logging_enabled BOOLEAN DEFAULT FALSE,
            humanlog_channel TEXT DEFAULT NULL,
            botlog_channel TEXT DEFAULT NULL
        )            
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS invitetracking (
            guild_id TEXT PRIMARY KEY,
            invite_tracking_enabled BOOLEAN DEFAULT FALSE,
            invitelog_channel TEXT DEFAULT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS invites (
            guild_id TEXT,
            invite_id TEXT,
            inviter_id TEXT,
            uses INTEGER,
            PRIMARY KEY (guild_id, invite_id)
        )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS birthday(
            user_id TEXT,
            guild_id TEXT,
            day INTEGER,
            month INTEGER,
            year INTEGER DEFAULT NULL,
            timezone TEXT ,
            PRIMARY KEY (user_id, guild_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS roles(
            guild_id TEXT ,
            role_id TEXT,
            role_name TEXT,
            is_bday_role BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (guild_id, role_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS birthday_users(
            user_id TEXT,
            guild_id TEXT,
            role_id TEXT,
            time_stamp REAL,
            PRIMARY KEY (user_id, guild_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS generator_channels(
            channel_id TEXT,
            guild_id TEXT,
            channel_name TEXT,
            PRIMARY KEY (channel_id, guild_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS authorized_users(
            user_id TEXT,
            guild_id TEXT,
            PRIMARY KEY (user_id, guild_id))""")
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS warn_setup(
            guild_id TEXT PRIMARY KEY,
            channel_id TEXT NOT NULL,
            channel_name TEXT)""")
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS warnings(
            user_id TEXT NOT NULL,
            guild_id TEXT NOT NULL,
            warns INTEGER DEFAULT 0,
            prev_warn TEXT DEFAULT NULL,
            PRIMARY KEY (user_id, guild_id))""")
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS afk(
            user_id TEXT NOT NULL,
            guild_id TEXT NOT NULL,
            reason TEXT DEFAULT NULL,
            since_timestamp REAL DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
            )""")
    c.execute("""
        CREATE TABLE IF NOT EXISTS archived_channels(
            channel_id TEXT NOT NULL,
            guild_id TEXT NOT NULL,
            category_id TEXT DEFAULT NULL,
            PRIMARY KEY (channel_id, guild_id)
            )""")
    
    print("✅ Database tables created successfully.")
    
    conn.commit()
    conn.close()    



