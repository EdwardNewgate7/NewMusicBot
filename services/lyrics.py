"""
╔══════════════════════════════════════════════════════════════╗
║      🎵 Harmony Music - Şarkı Sözleri Servisi v3.0       ║
║      Web scraping ile şarkı sözleri arama ve getirme        ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

import aiohttp

logger = logging.getLogger("LyricsService")


@dataclass
class LyricsResult:
    """Şarkı sözleri sonucu."""
    title: str = ""
    artist: str = ""
    lyrics: str = ""
    source: str = ""
    url: str = ""
    thumbnail: str = ""
    found: bool = False


async def search_lyrics(query: str) -> LyricsResult:
    """
    Şarkı sözlerini arar.
    Birden fazla kaynaktan arama yapar.

    Args:
        query: Aranacak şarkı adı / "sanatçı - şarkı"

    Returns:
        LyricsResult nesnesi
    """
    # Sırayla farklı kaynakları dene
    result = await _search_lyrics_api(query)
    if result and result.found:
        return result

    # Fallback - basit format döndür
    return LyricsResult(
        title=query,
        found=False,
    )


async def _search_lyrics_api(query: str) -> LyricsResult | None:
    """Lyrics.ovh API'si ile şarkı sözleri arar."""
    # Sanatçı ve şarkı adını ayırmaya çalış
    artist = ""
    title = query

    separators = [" - ", " – ", " — ", " | "]
    for sep in separators:
        if sep in query:
            parts = query.split(sep, 1)
            artist = parts[0].strip()
            title = parts[1].strip()
            break

    if not artist:
        # Sanatçı bulunamazsa doğrudan arama yap
        return await _search_some_lyrics(query)

    try:
        url = (
            f"https://api.lyrics.ovh/v1/"
            f"{quote_plus(artist)}/{quote_plus(title)}"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    lyrics_text = data.get("lyrics", "")
                    if lyrics_text:
                        # Sözleri temizle
                        lyrics_text = _clean_lyrics(lyrics_text)
                        return LyricsResult(
                            title=title,
                            artist=artist,
                            lyrics=lyrics_text,
                            source="lyrics.ovh",
                            found=True,
                        )
    except asyncio.TimeoutError:
        logger.warning("Lyrics API zaman aşımı.")
    except Exception as e:
        logger.error(f"Lyrics API hatası: {e}")

    return None


async def _search_some_lyrics(query: str) -> LyricsResult | None:
    """some-random-api ile şarkı sözleri arar (yedek kaynak)."""
    try:
        url = f"https://some-random-api.com/others/lyrics?title={quote_plus(query)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    title = data.get("title", query)
                    artist = data.get("author", "")
                    lyrics_text = data.get("lyrics", "")
                    thumbnail = ""

                    # Thumbnail al
                    thumbnail_data = data.get("thumbnail", {})
                    if isinstance(thumbnail_data, dict):
                        thumbnail = thumbnail_data.get("genius", "")

                    if lyrics_text:
                        lyrics_text = _clean_lyrics(lyrics_text)
                        return LyricsResult(
                            title=title,
                            artist=artist,
                            lyrics=lyrics_text,
                            source="some-random-api",
                            thumbnail=thumbnail,
                            found=True,
                        )
    except asyncio.TimeoutError:
        logger.warning("SomeRandomAPI lyrics zaman aşımı.")
    except Exception as e:
        logger.error(f"SomeRandomAPI lyrics hatası: {e}")

    return None


def _clean_lyrics(text: str) -> str:
    """Şarkı sözlerini temizler ve formatlar."""
    # Fazla boşlukları kaldır
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    # Çok uzun sözleri kırp (Telegram mesaj limiti)
    if len(text) > 3500:
        text = text[:3500] + "\n\n[... devamı kesildi]"

    return text


def split_lyrics(lyrics: str, max_length: int = 3800) -> list[str]:
    """
    Şarkı sözlerini Telegram mesaj limitine göre böler.

    Args:
        lyrics: Tam şarkı sözleri
        max_length: Maksimum parça uzunluğu

    Returns:
        Bölünmüş metin listesi
    """
    if len(lyrics) <= max_length:
        return [lyrics]

    parts = []
    current = ""

    for line in lyrics.split("\n"):
        if len(current) + len(line) + 1 > max_length:
            parts.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"

    if current.strip():
        parts.append(current.strip())

    return parts
