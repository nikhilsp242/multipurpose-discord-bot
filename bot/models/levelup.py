from database.connect import get_connection

class LevelUpConfig:
    def __init__(self, guild_id, booster_coin_multiplier = 1, booster_xp_multiplier = 1,levelup_enabled = False, vc_levelup_enabled = False, levelup_channel = None , enable_xp_for_all_channels = True,enable_coins_for_all_channels = True , custom_levelup_system = False):
        self.guild_id = guild_id
        self.booster_coin_multiplier = booster_coin_multiplier
        self.booster_xp_multiplier = booster_xp_multiplier
        self.levelup_enabled = levelup_enabled
        self.levelup_channel = levelup_channel
        self.enable_xp_for_all_channels = enable_xp_for_all_channels
        self.enable_coins_for_all_channels = enable_coins_for_all_channels
        self.vc_levelup_enabled = vc_levelup_enabled
        self.custom_levelup_system = custom_levelup_system

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

    @classmethod
    def get(cls, guild_id):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT *
                FROM levelup_settings
                WHERE guild_id = ?
            """, (guild_id,))
            row = c.fetchone()
            if row:
                return cls.from_db_row(row)
            else:
                return cls(guild_id)
        except Exception as e:
            print(f"Error fetching level up settings for guild {guild_id}: {e}")
            return None
        finally:
            conn.close()
    
    def save(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO levelup_settings (guild_id, booster_coin_multiplier, booster_xp_multiplier, levelup_enabled, levelup_channel, enable_xp_for_all_channels, enable_coins_for_all_channels, vc_levelup_enabled, custom_levelup_system)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    booster_xp_multiplier = excluded.booster_xp_multiplier,
                    booster_coin_multiplier = excluded.booster_coin_multiplier,
                    levelup_enabled = excluded.levelup_enabled,
                    levelup_channel = excluded.levelup_channel,
                    enable_xp_for_all_channels = excluded.enable_xp_for_all_channels,
                    enable_coins_for_all_channels = excluded.enable_coins_for_all_channels,
                    vc_levelup_enabled = excluded.vc_levelup_enabled,
                    custom_levelup_system = excluded.custom_levelup_system

            """, (self.guild_id, self.booster_coin_multiplier, self.booster_xp_multiplier, self.levelup_enabled, self.levelup_channel, self.enable_xp_for_all_channels, self.enable_coins_for_all_channels, self.vc_levelup_enabled, self.custom_levelup_system))
            conn.commit()
        except Exception as e:
            print(f"Error saving level up settings for guild {self.guild_id}: {e}")
        finally:
            conn.close()