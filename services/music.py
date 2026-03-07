"""
╔══════════════════════════════════════════════════════════════╗
║  🎵 Harmony Music - Gelişmiş YouTube Müzik Servisi v3.0  ║
║  Cookie.txt desteği, 320kbps ses, gelişmiş arama & indirme ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from pathlib import Path
from typing import Any

from config import config

logger = logging.getLogger("MusicService")

SERVICE_VERSION = "3.0.2-STABLE-DOWNLOAD"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     VERİ SINIFLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


from services.types import SongInfo, SearchResult

__all__ = [
    "SongInfo",
    "SearchResult",
    "validate_cookie_file",
    "search_youtube",
    "search_youtube_detailed",
    "download_song",
    "download_video",
    "extract_video_id",
    "is_youtube_url",
    "is_spotify_url",
    "get_spotify_metadata",
    "get_video_info",
    "format_duration",
    "format_views",
    "format_file_size",
    "clean_old_downloads",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                    COOKIE DOĞRULAMA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def validate_cookie_file() -> dict[str, Any]:
    """
    Cookie dosyasını doğrular ve durum bilgisi döndürür.

    Returns:
        {
            "valid": bool,
            "path": str | None,
            "line_count": int,
            "domain_count": int,
            "message": str,
        }
    """
    result = {
        "valid": False,
        "path": None,
        "line_count": 0,
        "domain_count": 0,
        "message": "",
    }

    if not config.COOKIE_ENABLED:
        result["message"] = "Cookie desteği devre dışı."
        return result

    cookie_path = config.get_cookie_path()
    if not cookie_path:
        result["message"] = (
            "Cookie dosyası bulunamadı veya boş. "
            f"Beklenen konum: {config.COOKIE_FILE}"
        )
        return result

    try:
        with open(cookie_path, "r", encoding="utf-8", errors="ignore") as f:
            # First line check for Netscape header
            first_line = f.readline()
            if not any(header in first_line for header in ["# Netscape", "# HTTP Cookie File"]):
                result["message"] = "⚠️ Geçersiz format: Cookie dosyası Netscape header'ı içermiyor."
                return result
            
            f.seek(0)
            lines = f.readlines()

        result["path"] = cookie_path
        result["line_count"] = len(lines)

        # Domain'leri say
        domains = set()
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # Netscape spec says tabs
                parts = line.split("\t")
                if len(parts) >= 7:
                    # Sanity check: second to last parts should be numbers/booleans usually
                    if parts[0].startswith(".") or "youtube" in parts[0]:
                        domains.add(parts[0])

        result["domain_count"] = len(domains)

        # YouTube domain kontrolü
        yt_domains = {
            d for d in domains
            if "youtube" in d or "google" in d or "googlevideo" in d
        }

        if yt_domains and len(lines) > 5:
            result["valid"] = True
            result["message"] = (
                f"✅ Cookie geçerli! {len(lines)} satır, "
                f"{len(domains)} domain ({len(yt_domains)} YouTube)."
            )
        else:
            result["message"] = (
                f"⚠️ Cookie dosyası {len(lines)} satır içeriyor "
                "ancak çok kısa veya YouTube domain'i bulunamadı."
            )

    except Exception as e:
        result["message"] = f"❌ Cookie dosyası okunamadı: {e}"

    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                    YOUTUBE ARAMA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def search_youtube(
    query: str,
    max_results: int = 5,
) -> list[SearchResult]:
    """
    YouTube'da şarkı arar (cookie.txt destekli).

    Args:
        query: Aranacak şarkı adı/sözleri
        max_results: Maksimum sonuç sayısı

    Returns:
        SearchResult listesi
    """
    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, _search_sync, query, max_results
        )
        return results
    except Exception as e:
        logger.error(f"YouTube arama hatası: {e}")
        return []


def _search_sync(query: str, max_results: int) -> list[SearchResult]:
    """Senkron YouTube arama (thread pool'da çalışır)."""
    import yt_dlp

    # Config'den temel opsiyonları al (cookie.txt dahil)
    ydl_opts = config.get_base_ytdlp_opts()
    ydl_opts.update({
        "extract_flat": True,
        "default_search": f"ytsearch{max_results}",
    })

    search_query = query
    if not query.startswith(("http://", "https://", "ytsearch")):
        search_query = f"ytsearch{max_results}:{query}"

    results = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)

        if not info:
            return results

        entries = info.get("entries", [])
        for entry in entries:
            if not entry:
                continue

            video_id = entry.get("id", "")
            title = entry.get("title", "Bilinmeyen")
            duration = entry.get("duration") or 0
            url = entry.get("webpage_url") or ""
            if not url:
                raw_url = entry.get("url") or ""
                if isinstance(raw_url, str) and raw_url.startswith("http"):
                    url = raw_url
                elif video_id:
                    url = f"https://youtube.com/watch?v={video_id}"
                elif raw_url:
                    url = f"https://youtube.com/watch?v={raw_url}"
            thumbnail = entry.get("thumbnail", "")
            channel = entry.get("channel", "") or entry.get("uploader", "")
            view_count = entry.get("view_count") or 0
            upload_date = entry.get("upload_date", "")

            # Sanatçı adını başlıktan çıkarmaya çalış
            artist = _extract_artist(title)

            results.append(SearchResult(
                title=title,
                artist=artist,
                duration=int(duration),
                url=url,
                thumbnail=thumbnail,
                video_id=video_id,
                channel=channel,
                view_count=view_count,
                upload_date=upload_date,
                is_live=entry.get("is_live", False),
            ))

    return results


async def search_youtube_detailed(
    query: str,
    max_results: int = 5,
) -> list[SearchResult]:
    """
    YouTube'da detaylı arama yapar (süre ve kanal bilgisi ile).
    Daha yavaş ama daha kapsamlı sonuçlar verir.
    """
    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, _search_detailed_sync, query, max_results
        )
        return results
    except Exception as e:
        logger.error(f"Detaylı YouTube arama hatası: {e}")
        return []


def _search_detailed_sync(
    query: str, max_results: int,
) -> list[SearchResult]:
    """Detaylı arama - extract_flat yerine tam bilgi alır."""
    import yt_dlp

    ydl_opts = config.get_base_ytdlp_opts()
    ydl_opts.update({
        "extract_flat": "in_playlist",
        "default_search": f"ytsearch{max_results}",
        "skip_download": True,
    })

    search_query = query
    if not query.startswith(("http://", "https://", "ytsearch")):
        search_query = f"ytsearch{max_results}:{query}"

    results = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        if not info:
            return results

        entries = info.get("entries", [])
        for entry in entries:
            if not entry:
                continue

            video_id = entry.get("id", "")
            title = entry.get("title", "Bilinmeyen")
            duration = entry.get("duration") or 0
            url = entry.get("webpage_url") or entry.get("url") or ""
            if not url:
                url = f"https://youtube.com/watch?v={video_id}"

            results.append(SearchResult(
                title=title,
                artist=_extract_artist(title),
                duration=int(duration),
                url=url,
                thumbnail=entry.get("thumbnail", ""),
                video_id=video_id,
                channel=(
                    entry.get("channel", "")
                    or entry.get("uploader", "")
                ),
                view_count=entry.get("view_count") or 0,
                upload_date=entry.get("upload_date", ""),
                is_live=entry.get("is_live", False),
            ))

    return results


def _extract_artist(title: str) -> str:
    """Şarkı başlığından sanatçı adını çıkarır."""
    separators = [" - ", " – ", " — ", " | ", " // "]
    for sep in separators:
        if sep in title:
            return title.split(sep)[0].strip()

    # "Artist ft. Artist2 Title" formatı
    ft_patterns = [" ft.", " ft ", " feat.", " feat ", " Ft.", " Feat."]
    for pattern in ft_patterns:
        if pattern in title:
            idx = title.index(pattern)
            return title[:idx].strip()

    return ""


def _pick_best_audio_format_id(info: dict[str, Any]) -> str | None:
    formats = info.get("formats") or []
    candidates: list[dict[str, Any]] = []
    for fmt in formats:
        if fmt.get("vcodec") != "none":
            continue
        if fmt.get("acodec") in (None, "none"):
            continue
        candidates.append(fmt)

    if not candidates:
        return None

    candidates.sort(
        key=lambda f: (
            f.get("abr") or 0,
            f.get("asr") or 0,
            f.get("tbr") or 0,
        ),
        reverse=True,
    )
    format_id = candidates[0].get("format_id")
    return str(format_id) if format_id else None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                    ŞARKI İNDİRME (MP3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def download_song(
    url: str,
    max_duration: int | None = None,
    quality: str | None = None,
    audio_format: str | None = None,
) -> SongInfo | None:
    """
    YouTube URL'sinden şarkıyı MP3/M4A olarak indirir.
    Cookie.txt otomatik olarak kullanılır.

    Args:
        url: YouTube video URL'si
        max_duration: Maksimum izin verilen süre (saniye)
        quality: Ses kalitesi override ("128", "192", "256", "320")
        audio_format: Format override ("mp3", "m4a", "opus", "flac")

    Returns:
        SongInfo veya None (başarısız ise)
    """
    if max_duration is None:
        max_duration = config.MAX_SONG_DURATION
    if quality is None:
        quality = config.AUDIO_QUALITY
    if audio_format is None:
        audio_format = config.AUDIO_FORMAT

    try:
        loop = asyncio.get_event_loop()
        song = await loop.run_in_executor(
            None, _download_sync, url, max_duration, quality, audio_format
        )
        return song
    except Exception as e:
        logger.error(f"İndirme hatası: {e}")
        return None


def _download_sync(
    url: str,
    max_duration: int,
    quality: str,
    audio_format: str,
) -> SongInfo | None:
    """Senkron indirme (thread pool'da çalışır) - cookie.txt destekli."""
    import yt_dlp

    config.ensure_dirs()
    download_dir = config.DOWNLOAD_PATH

    # Config'den temel opsiyonları al (cookie.txt dahil)
    ydl_opts = config.get_base_ytdlp_opts()
    ydl_opts.update({
        "format": "bestaudio/best",
        "outtmpl": os.path.join(download_dir, "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": quality,
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
        ],
        "max_filesize": config.MAX_AUDIO_FILE_SIZE,
        "writethumbnail": False,
        "embedthumbnail": False,
    })

    info_opts = dict(ydl_opts)
    info_opts.pop("format", None)
    info_opts["skip_download"] = True
    with yt_dlp.YoutubeDL(info_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        return None

    duration = info.get("duration") or 0
    if duration > max_duration:
        logger.warning(
            f"Şarkı çok uzun: {duration}s > {max_duration}s"
        )
        return None

    best_audio_format_id = _pick_best_audio_format_id(info)
    formats_to_try = [
        "bestaudio/best",
        best_audio_format_id,
        "bestaudio",
        "best",
    ]
    normalized_formats: list[str | None] = []
    for fmt in formats_to_try:
        if fmt and fmt not in normalized_formats:
            normalized_formats.append(fmt)
    # Ayrıca 'pop format' seçeneği için None ekle (en son çare)
    normalized_formats.append(None)

    cookie_profiles = [True]
    if ydl_opts.get("cookiefile"):
        cookie_profiles.append(False)
    last_error: Exception | None = None
    for use_cookie in cookie_profiles:
        for selected_format in normalized_formats:
            try:
                attempt_opts = dict(ydl_opts)
                if selected_format is None:
                    attempt_opts.pop("format", None)
                else:
                    attempt_opts["format"] = selected_format
                if not use_cookie:
                    attempt_opts.pop("cookiefile", None)
                attempt_opts["skip_download"] = False
                with yt_dlp.YoutubeDL(attempt_opts) as attempt_ydl:
                    attempt_ydl.download([url])
                last_error = None
                break
            except yt_dlp.utils.DownloadError as exc:
                last_error = exc
                if "Requested format is not available" not in str(exc):
                    raise
        if last_error is None:
            break

    if last_error:
        raise last_error

    video_id = info.get("id", "")
    file_path = os.path.join(
        download_dir, f"{video_id}.{audio_format}"
    )

    if not os.path.exists(file_path):
        for ext in ["mp3", "m4a", "webm", "opus", "ogg", "flac"]:
            alt_path = os.path.join(download_dir, f"{video_id}.{ext}")
            if os.path.exists(alt_path):
                file_path = alt_path
                break

    if not os.path.exists(file_path):
        logger.error(f"İndirilen dosya bulunamadı: {file_path}")
        return None

    title = info.get("title", "Bilinmeyen")
    artist = _extract_artist(title)
    thumbnail = info.get("thumbnail", "")
    file_size = os.path.getsize(file_path)

    return SongInfo(
        title=title,
        artist=artist or info.get("artist", "") or info.get("creator", ""),
        duration=int(duration),
        url=info.get("webpage_url", url),
        thumbnail=thumbnail,
        file_path=file_path,
        file_size=file_size,
        source="youtube",
        video_id=video_id,
        album=info.get("album", ""),
        upload_date=info.get("upload_date", ""),
        view_count=info.get("view_count") or 0,
        like_count=info.get("like_count") or 0,
        channel=info.get("channel", "") or info.get("uploader", ""),
        quality=f"{quality}kbps {audio_format.upper()}",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                    VİDEO İNDİRME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def download_video(
    url: str,
    max_duration: int | None = None,
    quality: str | None = None,
) -> SongInfo | None:
    """
    YouTube URL'sinden videoyu indirir (cookie.txt destekli).

    Args:
        url: YouTube video URL'si
        max_duration: Maksimum izin verilen süre (saniye)
        quality: Video kalitesi override ("360", "480", "720", "1080")

    Returns:
        SongInfo veya None
    """
    if max_duration is None:
        max_duration = config.MAX_SONG_DURATION
    if quality is None:
        quality = config.VIDEO_QUALITY

    try:
        loop = asyncio.get_event_loop()
        video = await loop.run_in_executor(
            None, _download_video_sync, url, max_duration, quality
        )
        return video
    except Exception as e:
        logger.error(f"Video indirme hatası: {e}")
        return None


def _download_video_sync(
    url: str, max_duration: int, quality: str,
) -> SongInfo | None:
    """Senkron video indirme - cookie.txt destekli."""
    import yt_dlp

    config.ensure_dirs()
    download_dir = config.DOWNLOAD_PATH

    # Config'den temel opsiyonları al (cookie.txt dahil)
    ydl_opts = config.get_base_ytdlp_opts()
    ydl_opts.update({
        "format": (
            f"bv*[height<={quality}]+ba/"
            f"b[height<={quality}]/"
            f"best[height<={quality}]/"
            "bv*+ba/best"
        ),
        "outtmpl": os.path.join(download_dir, "%(id)s.%(ext)s"),
        "max_filesize": config.MAX_VIDEO_FILE_SIZE,
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            },
        ],
    })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    if not info:
        return None

    duration = info.get("duration") or 0
    if duration > max_duration:
        return None

    formats_to_try = [
        ydl_opts["format"],
        f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]",
        "bestvideo+bestaudio/best",
        "best",
    ]
    last_error: Exception | None = None
    for selected_format in formats_to_try:
        try:
            attempt_opts = dict(ydl_opts)
            attempt_opts["format"] = selected_format
            with yt_dlp.YoutubeDL(attempt_opts) as attempt_ydl:
                attempt_ydl.download([url])
            last_error = None
            break
        except yt_dlp.utils.DownloadError as exc:
            last_error = exc
            if "Requested format is not available" not in str(exc):
                raise

    if last_error:
        raise last_error

    video_id = info.get("id", "")
    file_path = ""
    for ext in ["mp4", "webm", "mkv", "avi"]:
        candidate = os.path.join(download_dir, f"{video_id}.{ext}")
        if os.path.exists(candidate):
            file_path = candidate
            break

    if not file_path:
        return None

    title = info.get("title", "Bilinmeyen")

    return SongInfo(
        title=title,
        artist=_extract_artist(title),
        duration=int(duration),
        url=info.get("webpage_url", url),
        thumbnail=info.get("thumbnail", ""),
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        source="youtube",
        video_id=video_id,
        channel=info.get("channel", "") or info.get("uploader", ""),
        quality=f"{quality}p",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                    URL VE VİDEO ID AYIKLAMA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def extract_video_id(url: str) -> str | None:
    """YouTube URL'sinden video ID'sini çıkarır."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def is_youtube_url(text: str) -> bool:
    """Metnin YouTube linki olup olmadığını kontrol eder."""
    yt_pattern = re.compile(
        r"https?://(?:www\.)?(?:youtube\.com/(?:watch|shorts)|youtu\.be/)"
        r"[\w?=&-]+",
        re.IGNORECASE,
    )
    return bool(yt_pattern.search(text))


def is_spotify_url(text: str) -> bool:
    """Metnin Spotify linki olup olmadığını kontrol eder."""
    sp_pattern = re.compile(
        r"https?://open\.spotify\.com/(track|album|playlist)/[\w]+",
        re.IGNORECASE,
    )
    return bool(sp_pattern.search(text))

async def get_spotify_metadata(url: str) -> tuple[str, str, str | None]:
    """
    Spotify URL'sinden metadata çeker.
    Returns: (title, artist, search_query)
    """
    try:
        import yt_dlp
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_sp_sync, url)
    except Exception as e:
        logger.error(f"Spotify metada hatası: {e}")
        return ("Bilinmeyen", "Bilinmeyen", None)

def _get_sp_sync(url: str) -> tuple[str, str, str | None]:
    import yt_dlp
    ydl_opts = {"quiet": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info:
                return ("Bilinmeyen", "Bilinmeyen", None)
            
            title = info.get("title") or info.get("track") or "Bilinmeyen"
            artist = info.get("artist") or info.get("creator") or info.get("uploader") or "Bilinmeyen"
            
            # YouTube arama kelimesi oluştur
            search_query = f"{artist} - {title}" if artist != "Bilinmeyen" else title
            return (title, artist, search_query)
        except Exception:
            return ("Bilinmeyen", "Bilinmeyen", None)


async def get_video_info(url: str) -> SongInfo | None:
    """
    Video bilgilerini indiirmeden alır.
    """
    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None, _get_info_sync, url
        )
        return info
    except Exception as e:
        logger.error(f"Video bilgi alma hatası: {e}")
        return None


def _get_info_sync(url: str) -> SongInfo | None:
    """Senkron bilgi alma."""
    import yt_dlp

    ydl_opts = config.get_base_ytdlp_opts()
    ydl_opts["skip_download"] = True

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info:
            return None

        title = info.get("title", "Bilinmeyen")
        return SongInfo(
            title=title,
            artist=_extract_artist(title) or info.get("artist", ""),
            duration=info.get("duration") or 0,
            url=info.get("webpage_url", url),
            thumbnail=info.get("thumbnail", ""),
            video_id=info.get("id", ""),
            source="youtube",
            album=info.get("album", ""),
            upload_date=info.get("upload_date", ""),
            view_count=info.get("view_count") or 0,
            like_count=info.get("like_count") or 0,
            channel=info.get("channel", "") or info.get("uploader", ""),
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                  FORMAT YARDIMCILARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def format_duration(seconds: int) -> str:
    """Süreyi 'MM:SS' veya 'HH:MM:SS' formatına çevirir."""
    if seconds <= 0:
        return "0:00"
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_views(count: int) -> str:
    """Görüntülenme sayısını formatlı yapar."""
    if count >= 1_000_000_000:
        return f"{count / 1_000_000_000:.1f}B"
    elif count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def format_file_size(size_bytes: int) -> str:
    """Dosya boyutunu formatlı yapar."""
    if size_bytes >= 1024 * 1024 * 1024:
        return f"{size_bytes / (1024**3):.1f}GB"
    elif size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024**2):.1f}MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f}KB"
    return f"{size_bytes}B"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   TEMİZLİK İŞLEMLERİ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def clean_old_downloads() -> int:
    """Eski indirmeleri temizler, silinen dosya sayısını döndürür."""
    import time

    download_dir = Path(config.DOWNLOAD_PATH)
    if not download_dir.exists():
        return 0

    max_age = config.AUTO_CLEANUP_SECONDS
    if max_age <= 0:
        return 0

    now = time.time()
    count = 0
    for f in download_dir.iterdir():
        if f.is_file() and (now - f.stat().st_mtime) > max_age:
            try:
                f.unlink()
                count += 1
            except OSError:
                pass

    if count > 0:
        logger.info(f"🗑️ {count} eski indirme dosyası temizlendi.")
    return count


def get_download_dir_size() -> int:
    """İndirme dizininin toplam boyutunu döndürür (byte)."""
    download_dir = Path(config.DOWNLOAD_PATH)
    if not download_dir.exists():
        return 0
    return sum(f.stat().st_size for f in download_dir.iterdir() if f.is_file())


def get_download_file_count() -> int:
    """İndirme dizinindeki dosya sayısını döndürür."""
    download_dir = Path(config.DOWNLOAD_PATH)
    if not download_dir.exists():
        return 0
    return sum(1 for f in download_dir.iterdir() if f.is_file())
