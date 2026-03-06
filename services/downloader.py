"""
╔══════════════════════════════════════════════════════════════╗
║   🎵 Harmony Music - Çoklu Platform Medya İndirici v3.0  ║
║   Cookie.txt destekli medya indirme servisi                 ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

from config import config

logger = logging.getLogger("DownloaderService")


@dataclass
class MediaInfo:
    """İndirilen medya bilgileri."""
    platform: str = ""          # instagram, youtube, tiktok, vb.
    media_type: str = ""        # photo, video, audio, story
    title: str = ""
    file_path: str = ""
    file_size: int = 0
    thumbnail: str = ""
    url: str = ""
    duration: int = 0


# ── Platform URL Kalıpları ─────────────────────────────────────

PLATFORM_PATTERNS: dict[str, re.Pattern] = {
    "instagram": re.compile(
        r"https?://(?:www\.)?instagram\.com/"
        r"(?:p|reel|stories|tv)/[\w-]+",
        re.IGNORECASE,
    ),
    "youtube": re.compile(
        r"https?://(?:www\.)?(?:youtube\.com/(?:watch|shorts)|youtu\.be/)"
        r"[\w?=&-]+",
        re.IGNORECASE,
    ),
    "tiktok": re.compile(
        r"https?://(?:www\.|vm\.)?tiktok\.com/[\w@/.-]+",
        re.IGNORECASE,
    ),
    "facebook": re.compile(
        r"https?://(?:www\.|m\.)?facebook\.com/"
        r"(?:watch|reel|[\w.]+/(?:videos|posts))/[\w/?=&.-]+",
        re.IGNORECASE,
    ),
    "pinterest": re.compile(
        r"https?://(?:www\.|tr\.)?pinterest\.com/pin/[\w-]+",
        re.IGNORECASE,
    ),
    "snapchat": re.compile(
        r"https?://(?:www\.)?snapchat\.com/[\w/.-]+",
        re.IGNORECASE,
    ),
    "telegram": re.compile(
        r"https?://t\.me/[\w/]+",
        re.IGNORECASE,
    ),
    "likee": re.compile(
        r"https?://(?:www\.|l\.)?likee\.video/[\w/.-]+",
        re.IGNORECASE,
    ),
    "threads": re.compile(
        r"https?://(?:www\.)?threads\.net/[\w@/.-]+",
        re.IGNORECASE,
    ),
    "twitter": re.compile(
        r"https?://(?:www\.)?(?:twitter|x)\.com/[\w]+/status/\d+",
        re.IGNORECASE,
    ),
    "spotify": re.compile(
        r"https?://open\.spotify\.com/track/[\w]+",
        re.IGNORECASE,
    ),
    "soundcloud": re.compile(
        r"https?://(?:www\.)?soundcloud\.com/[\w-]+/[\w-]+",
        re.IGNORECASE,
    ),
}


def detect_platform(url: str) -> str | None:
    """URL'den platformu tespit eder."""
    for platform, pattern in PLATFORM_PATTERNS.items():
        if pattern.search(url):
            return platform
    return None


def extract_urls(text: str) -> list[tuple[str, str]]:
    """
    Mesaj metninden desteklenen platform URL'lerini çıkarır.
    Returns: (url, platform) tuple listesi
    """
    results = []
    for platform, pattern in PLATFORM_PATTERNS.items():
        matches = pattern.findall(text)
        for match in matches:
            results.append((match, platform))
    return results


async def download_media(url: str) -> MediaInfo | None:
    """
    Verilen URL'den medyayı indirir (cookie.txt destekli).
    """
    platform = detect_platform(url)
    if not platform:
        return None

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, _download_media_sync, url, platform
        )
        return result
    except Exception as e:
        logger.error(f"Medya indirme hatası ({platform}): {e}")
        return None


def _download_media_sync(url: str, platform: str) -> MediaInfo | None:
    """Senkron medya indirme - cookie.txt destekli."""
    import yt_dlp

    config.ensure_dirs()
    download_dir = config.DOWNLOAD_PATH

    # Config'den temel opsiyonları al (cookie.txt dahil)
    ydl_opts = config.get_base_ytdlp_opts()
    ydl_opts.update({
        "format": (
            f"bv*[height<={config.VIDEO_QUALITY}]+ba/"
            f"b[height<={config.VIDEO_QUALITY}]/"
            f"best[height<={config.VIDEO_QUALITY}]/"
            "bv*+ba/best"
        ),
        "outtmpl": os.path.join(download_dir, "media_%(id)s.%(ext)s"),
        "max_filesize": config.MAX_VIDEO_FILE_SIZE,
    })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None

            video_id = info.get("id", "unknown")
            ext = info.get("ext", "mp4")
            file_path = os.path.join(
                download_dir, f"media_{video_id}.{ext}"
            )

            if not os.path.exists(file_path):
                # Alternatif dosya adlarını dene
                for f in os.listdir(download_dir):
                    if f.startswith(f"media_{video_id}"):
                        file_path = os.path.join(download_dir, f)
                        break

            if not os.path.exists(file_path):
                return None

            return MediaInfo(
                platform=platform,
                media_type=(
                    "video" if ext in ("mp4", "webm", "mkv")
                    else "photo" if ext in ("jpg", "png", "webp")
                    else "audio"
                ),
                title=info.get("title", ""),
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                thumbnail=info.get("thumbnail", ""),
                url=url,
                duration=info.get("duration") or 0,
            )
    except Exception as e:
        logger.error(f"yt-dlp indirme hatası: {e}")
        return None


# Platform emoji eşleme
PLATFORM_EMOJI = {
    "instagram": "📸",
    "youtube": "▶️",
    "tiktok": "🎵",
    "facebook": "📘",
    "pinterest": "📌",
    "snapchat": "👻",
    "telegram": "✈️",
    "likee": "❤️",
    "threads": "🧵",
    "twitter": "🐦",
    "spotify": "🎧",
    "soundcloud": "🔊",
}


def get_platform_name(platform: str) -> str:
    """Platform adını büyük harflerle döndürür."""
    names = {
        "instagram": "INSTAGRAM",
        "youtube": "YOUTUBE",
        "tiktok": "TIKTOK",
        "facebook": "FACEBOOK",
        "pinterest": "PINTEREST",
        "snapchat": "SNAPCHAT",
        "telegram": "TELEGRAM",
        "likee": "LIKEE",
        "threads": "THREADS",
        "twitter": "TWITTER / X",
        "spotify": "SPOTIFY",
        "soundcloud": "SOUNDCLOUD",
    }
    return names.get(platform, platform.upper())
