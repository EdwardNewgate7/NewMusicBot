"""
Harmony Music - Medya Link Tespit Router'ı
Gruptaki mesajlarda otomatik olarak desteklenen platform
linklerini tespit eder ve medyayı indirir.
"""

from __future__ import annotations

import logging
import os

from aiogram import F, Router
from aiogram.types import FSInputFile, Message

from services.downloader import (
    PLATFORM_EMOJI,
    download_media,
    extract_urls,
    get_platform_name,
)
from utils.emoji_ids import emoji

router = Router(name="media_detector")
logger = logging.getLogger("MediaDetector")


@router.message(F.text.regexp(r"https?://"))
async def detect_media_link(message: Message) -> None:
    """
    Mesajlardaki medya linklerini otomatik tespit eder ve indirir.
    """
    if not message.text:
        return

    # URL'leri tespit et
    urls = extract_urls(message.text)
    if not urls:
        return

    for url, platform in urls:
        platform_emoji = PLATFORM_EMOJI.get(platform, "🔗")
        platform_name = get_platform_name(platform)

        # İndirme başlıyor mesajı
        status_msg = await message.reply(
            text=(
                f'{platform_emoji} <b>{platform_name}</b>\n\n'
                f'<tg-emoji emoji-id="{emoji.HEART_DOWNLOAD}">💗</tg-emoji>'
                " <b>İNDİRİLİYOR...</b>\n"
                "<i>Lütfen bekleyin...</i>"
            ),
            parse_mode="HTML",
        )

        # Medyayı indir
        media = await download_media(url)

        if media is None:
            await status_msg.edit_text(
                text=(
                    f'{platform_emoji} <b>{platform_name}</b>\n\n'
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    " <b>İNDİRME BAŞARISIZ.</b>\n"
                    "<i>Bu içerik indirilemedi veya desteklenmiyor.</i>"
                ),
                parse_mode="HTML",
            )
            continue

        # Dosya boyutu kontrolü (Telegram limiti: 50MB)
        if media.file_size > 50 * 1024 * 1024:
            await status_msg.edit_text(
                text=(
                    f'{platform_emoji} <b>{platform_name}</b>\n\n'
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    " <b>DOSYA ÇOK BÜYÜK!</b>\n"
                    f"<i>Boyut: {media.file_size // (1024*1024)}MB "
                    "(Limit: 50MB)</i>"
                ),
                parse_mode="HTML",
            )
            # Dosyayı temizle
            _cleanup_file(media.file_path)
            continue

        try:
            file = FSInputFile(media.file_path)
            size_mb = round(media.file_size / (1024 * 1024), 1)

            caption = (
                f'{platform_emoji} <b>{platform_name}</b>\n'
            )
            if media.title:
                caption += f"📝 <b>{media.title}</b>\n"
            caption += (
                f"📦 <b>Boyut:</b> {size_mb}MB\n\n"
                f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
                " <b>HARMONY MUSIC</b>"
            )

            if media.media_type == "video":
                await message.reply_video(
                    video=file,
                    caption=caption,
                    parse_mode="HTML",
                )
            elif media.media_type == "photo":
                await message.reply_photo(
                    photo=file,
                    caption=caption,
                    parse_mode="HTML",
                )
            elif media.media_type == "audio":
                await message.reply_audio(
                    audio=file,
                    caption=caption,
                    parse_mode="HTML",
                )
            else:
                await message.reply_document(
                    document=file,
                    caption=caption,
                    parse_mode="HTML",
                )

            # Başarılı - status mesajını sil
            await status_msg.delete()

        except Exception as e:
            logger.error(f"Dosya gönderme hatası: {e}")
            await status_msg.edit_text(
                text=(
                    f'{platform_emoji} <b>{platform_name}</b>\n\n'
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    " <b>GÖNDERME HATASI.</b>\n"
                    f"<i>{str(e)[:100]}</i>"
                ),
                parse_mode="HTML",
            )
        finally:
            # Dosyayı temizle
            _cleanup_file(media.file_path)


def _cleanup_file(path: str) -> None:
    """Geçici dosyayı temizler."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
