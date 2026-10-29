# Kaoru Discord Bot

Kaoru is a Discord server bot built with `discord.py` and SQLite. It is organized as a set of cogs and includes moderation, server utilities, leveling and user stats, birthdays, invite tracking, temporary voice channels, and other community features.

This repository covers the bot. The unfinished `web/` dashboard/API is intentionally excluded.

## Project layout

- `bot/main.py` — loads extensions from `bot/cogs/` and starts the bot.
- `bot/cogs/` — bot features, grouped by area.
- `bot/models/` — data models used by features.
- `bot/database/` — SQLite schema setup and update helpers.
- `bot/utils/` — shared bot helpers.
- `bot/data/` — local runtime data; database files are not tracked.

## Setup

1. Install Python and the dependencies used by the bot. This project currently has no dependency manifest, so dependencies must be identified from the imports in the bot code and installed in your environment.
2. Create a local `bot/config.py`. This file is ignored by Git because it contains deployment-specific settings and credentials. It must define at least `TOKEN` (the Discord bot token) and `PREFIXS` (a list of command prefixes). The leveling settings `coinsPerMessage`, `xpPerMessage`, and `xpPerMin` are also read by the bot. Optional third-party API keys may be needed by individual features.
3. From the `bot/` directory, run:

   ```bash
   python main.py
   ```

The bot expects its working directory to be `bot/`; its database paths are relative to that directory. Database schema setup is currently not run automatically by `main.py`, so use the existing database setup procedure for a fresh deployment.

## Security and data

Never commit bot tokens, API keys, passwords, local databases, or server/member data. Rotate any credentials that have previously been exposed, and keep the replacements in your ignored local configuration. The bot requests all Discord gateway intents; enable the intents it needs in the Discord Developer Portal and review the code before granting permissions in a server.

## Status

This is a personal bot project with a broad set of implemented features. There is no automated test suite or dependency manifest in the repository at this time.
