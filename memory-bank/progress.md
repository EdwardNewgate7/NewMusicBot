# Progress: Harmony Music Bot

## What Works
- **Core Bot**: aiogram setup, command routing, middleware.
- **Music Playback**: YouTube search, high-quality download, assistant streaming.
- **Media Download**: Support for Instagram, TikTok, etc.
- **UI**: Custom emojis, colorful buttons, search result selection.
- **Features**: Tagging system, scoring, statistics, playlists.
- **Stability**: yt-dlp client rotatation, cookie.txt auto-download.

## What's Left to Build
- Enhanced Quiz logic for `/yarisma`.
- More platform support in `media_detector.py`.
- Advanced admin settings via inline menus.

- Fixed a `NameError` in `main.py` and `ImportError` in `routers/music.py`.
- Verified that local code is correct, but container needs redeployment to sync.
- Current Status: Stable locally, awaiting cloud sync.

## Known Issues
- Music playback can fail if `yt-dlp` is blocked by YouTube (partially fixed with client rotation).
- Circular import container crash loops when Railway automatically retries an old deployment over and over.
