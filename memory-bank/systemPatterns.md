# System Patterns

## Architecture
- **aiogram 3.x**: Main framework for handling Telegram Bot API (commands, callbacks, inline queries).
- **PyTgCalls**: Assistant client that streams audio/video in Telegram Voice Chats.
- **SQLite Database**: Local lightweight storage (`aiosqlite` for async), managing users, groups, playlists, and message statistics.
- **Middleware System**: Uses `ThrottlingMiddleware` to prevent spam, and `StatsMiddleware` to automatically record all user messages for the internal ranking system.

## Design Decisions
- **Custom Emojis**: Replaced text-based UI with rich graphical buttons via `icon_custom_emoji_id` mapped in `utils/emoji_ids.py`.
- **Modularity**: Code is split across `routers/` for logical segregation (e.g., `music.py`, `admin.py`, `fun.py`, `scorer.py`).
- **Resilience**: The assistant runs with `in_memory=True` (for session strings) to ensure SQLite won't lock up during Docker deployments (e.g., on Railway) while running concurrently with the main bot.

## Deployment Strategy
- Docker-based build process (`Dockerfile`) ensuring `ffmpeg` is available on the system.
- `railway.json` and `Procfile` define the default `startCommand` for easy cloud distribution.
