"""
╔══════════════════════════════════════════════════════════════╗
║       🎵 Harmony Music - Inline Mod Router v3.0            ║
║       @BotUsername şarkı adı ile arama + paylaşım            ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import hashlib
import logging
from uuid import uuid4

from aiogram import Router
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from services.music import format_duration, search_youtube
from utils.emoji_ids import emoji

router = Router(name="inline")
logger = logging.getLogger("InlineMode")


@router.inline_query()
async def inline_search(inline_query: InlineQuery) -> None:
    """
    Inline şarkı arama handler'ı.
    Kullanıcı @BotUsername <şarkı adı> yazdığında tetiklenir.
    """
    query = inline_query.query.strip()

    if len(query) < 2:
        # Çok kısa sorgu, yardım göster
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="🎵 Şarkı Ara",
                    description="Aranacak şarkı adını yazın...",
                    input_message_content=InputTextMessageContent(
                        message_text=(
                            f'<tg-emoji emoji-id="{emoji.MUSIC_NOTE}">'
                            "🎵</tg-emoji>"
                            " <b>HARMONY MUSIC v3.0</b>\n\n"
                            "Inline modda şarkı aramak için:\n"
                            "<code>@BotUsername şarkı adı</code>\n\n"
                            "🎚 <b>320kbps</b> yüksek kaliteli ses\n"
                            "🍪 Cookie.txt desteği\n"
                            "📝 Şarkı sözleri bulma"
                        ),
                        parse_mode="HTML",
                    ),
                ),
            ],
            cache_time=10,
            is_personal=True,
        )
        return

    # YouTube'da ara
    logger.info(
        f"Inline arama: '{query}' (kullanıcı: {inline_query.from_user.id})"
    )
    results = await search_youtube(query, max_results=10)

    if not results:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="❌ Sonuç Bulunamadı",
                    description=f"'{query}' için sonuç bulunamadı.",
                    input_message_content=InputTextMessageContent(
                        message_text=(
                            f'<tg-emoji emoji-id="{emoji.STOP}">'
                            "⛔</tg-emoji>"
                            f" <b>'{query}' İÇİN SONUÇ BULUNAMADI.</b>"
                        ),
                        parse_mode="HTML",
                    ),
                ),
            ],
            cache_time=10,
            is_personal=True,
        )
        return

    articles = []
    for i, song in enumerate(results):
        duration_str = format_duration(song.duration)
        artist_display = song.artist or song.channel or "Bilinmeyen Sanatçı"

        # Her sonuç için benzersiz ID
        result_id = hashlib.md5(
            f"{song.video_id}{i}".encode()
        ).hexdigest()

        # Paylaşıma uygun mesaj (gruba gönderilecek)
        inline_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="OYNAT",
                        url=f"https://t.me/{inline_query.bot.username}?start=play_{song.video_id}",
                        icon_custom_emoji_id=emoji.PLAY,
                        style="success",
                    ),
                    InlineKeyboardButton(
                        text="İNDİR",
                        url=f"https://t.me/{inline_query.bot.username}?start=dl_{song.video_id}",
                        icon_custom_emoji_id=emoji.HEART_DOWNLOAD,
                        style="primary",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="YOUTUBE'DA İZLE",
                        url=song.url,
                        icon_custom_emoji_id=emoji.LINK,
                        style="danger",
                    ),
                ],
            ]
        )

        articles.append(
            InlineQueryResultArticle(
                id=result_id,
                title=f"🎵 {song.title}",
                description=f"👤 {artist_display} • ⏱ {duration_str}",
                thumbnail_url=song.thumbnail or None,
                input_message_content=InputTextMessageContent(
                    message_text=(
                        f'<tg-emoji emoji-id="{emoji.MUSIC_NOTE}">'
                        "🎵</tg-emoji>"
                        f" <b>{song.title}</b>\n\n"
                        f"👤 <b>Sanatçı:</b> {artist_display}\n"
                        f"⏱ <b>Süre:</b> {duration_str}\n"
                        f"🔗 <b>Link:</b> {song.url}\n\n"
                        "<i>Gruba ekleyip</i> "
                        f"<code>/oynat {song.url}</code> <i>yazın.</i>\n\n"
                        f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
                        " <i>Harmony Music v3.0 ile paylaşıldı.</i>"
                    ),
                    parse_mode="HTML",
                ),
                reply_markup=inline_keyboard,
            )
        )

    await inline_query.answer(
        results=articles,
        cache_time=60,
        is_personal=False,
    )
