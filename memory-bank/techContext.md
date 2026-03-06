# Tech Context: Harmony Music Bot

## Technologies Used
- **Core**: Python 3.10+
- **Bot Framework**: aiogram 3.x (Asyncio based)
- **Voice Chat**: PyTgCalls (with Pyrogram)
- **Downloader**: yt-dlp (with FFMPEG)
- **Database**: SQLite (via aiosqlite)
- **Logging**: Python standard logging with FileHandler

## Development Setup
- **OS**: Windows (Local development)
- **Dependencies**: Listed in `requirements.txt`
- **Environment**: `.env` file for tokens and paths

## Technical Constraints
- **FFMPEG**: Required for audio extraction and conversion.
- **yt-dlp**: Must be updated regularly to bypass YouTube blocks.
- **Cookies**: required for age-restricted content.
- **CPU/RAM**: Voice chat streaming is relatively resource-intensive.

## Tool Usage Patterns
- `yt-dlp` used with multiple clients (`android`, `web`, `ios`) for resilience.
- Assistant uses `in_memory=True` for session storage to avoid file locks.
