"""
Harmony Music - Çalma Listesi Router'ı (Veritabanı Entegreli)
/ekle, /cikar, /playlist, /listemisil komutları - gerçek SQLite ile.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import config
from database.models import (
    add_to_playlist,
    clear_playlist,
    get_playlist,
    get_playlist_count,
    remove_from_playlist,
    remove_from_playlist_by_title,
)
from services.music import format_duration, search_youtube
from utils.emoji_ids import emoji
from utils.keyboards import get_playlist_manage_keyboard

router = Router(name="playlist")


@router.message(Command("ekle", "add", "append"))
async def cmd_ekle(message: Message) -> None:
    """
    /ekle [ŞARKI ADI] komutu.
    YouTube'da arar ve çalma listesine ekler.
    """
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN EKLENECEK ŞARKI ADINI YAZIN.</b>\n\n"
                "<b>Kullanım:</b> <code>/ekle şarkı adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    query = args[1]
    user_id = message.from_user.id

    # Limit kontrolü
    count = await get_playlist_count(user_id)
    if count >= config.MAX_PLAYLIST_SIZE:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                f" <b>ÇALMA LİSTEN DOLU!</b>\n"
                f"Maksimum: {config.MAX_PLAYLIST_SIZE} şarkı.\n"
                "Yer açmak için: <code>/cikar şarkı adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    # YouTube'da ara
    status_msg = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>ARANIYOR:</b> <code>{query[:50]}</code>"
        ),
        parse_mode="HTML",
    )

    results = await search_youtube(query, max_results=1)

    if not results:
        await status_msg.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>ŞARKI BULUNAMADI.</b>"
            ),
            parse_mode="HTML",
        )
        return

    song = results[0]

    # Veritabanına ekle
    song_id = await add_to_playlist(
        user_id=user_id,
        title=song.title,
        artist=song.artist,
        url=song.url,
        duration=song.duration,
    )

    new_count = await get_playlist_count(user_id)

    await status_msg.edit_text(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>LİSTEYE EKLENDİ!</b>\n\n"
            f"🎵 <b>{song.title}</b>\n"
            f"👤 {song.artist or 'Bilinmeyen'}\n"
            f"⏱ {format_duration(song.duration)}\n\n"
            f"📋 Listen: {new_count}/{config.MAX_PLAYLIST_SIZE}"
        ),
        parse_mode="HTML",
    )


@router.message(Command("cikar", "remove", "delete", "del"))
async def cmd_cikar(message: Message) -> None:
    """
    /cikar [ŞARKI/NO] komutu.
    Çalma listesinden şarkı siler.
    """
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN ÇIKARILACAK ŞARKI ADINI VEYA "
                "NUMARASINI YAZIN.</b>\n\n"
                "<b>Kullanım:</b> <code>/cikar şarkı adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    query = args[1]
    user_id = message.from_user.id

    # Numara mı kontrol et
    if query.isdigit():
        playlist = await get_playlist(user_id)
        idx = int(query) - 1
        if 0 <= idx < len(playlist):
            song = playlist[idx]
            removed = await remove_from_playlist(user_id, song["id"])
            if removed:
                await message.answer(
                    text=(
                        f'<tg-emoji emoji-id="{emoji.CHECKMARK}">☑️</tg-emoji>'
                        f" <b>LİSTEDEN ÇIKARILDI:</b>\n"
                        f"🎵 {song['title']}"
                    ),
                    parse_mode="HTML",
                )
                return

    # İsimle ara ve sil
    removed = await remove_from_playlist_by_title(user_id, query)
    if removed:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.CHECKMARK}">☑️</tg-emoji>'
                f" <b>LİSTEDEN ÇIKARILDI:</b> {query}"
            ),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                f" <b>ŞARKI BULUNAMADI:</b> {query}"
            ),
            parse_mode="HTML",
        )


@router.message(Command("playlist", "liste", "list", "mylist"))
async def cmd_playlist(message: Message) -> None:
    """
    /playlist komutu.
    Çalma listesini görüntüler.
    """
    user_id = message.from_user.id
    playlist = await get_playlist(user_id)

    if not playlist:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.DISK}">💿</tg-emoji>'
                " <b>ÇALMA LİSTEN BOŞ!</b>\n\n"
                "Şarkı eklemek için:\n"
                "<code>/ekle şarkı adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    text_parts = [
        f'<tg-emoji emoji-id="{emoji.DISK}">💿</tg-emoji>'
        f" <b>ÇALMA LİSTEN ({len(playlist)} şarkı):</b>\n\n"
    ]

    for i, song in enumerate(playlist[:20], 1):
        dur = format_duration(song["duration"])
        artist = song["artist"] or "Bilinmeyen"
        text_parts.append(
            f"  <b>{i}.</b> {song['title']}\n"
            f"     👤 {artist} • ⏱ {dur}\n"
        )

    if len(playlist) > 20:
        text_parts.append(
            f"\n<i>...ve {len(playlist) - 20} şarkı daha</i>"
        )

    text_parts.append(
        f"\n📋 {len(playlist)}/{config.MAX_PLAYLIST_SIZE}"
    )

    await message.answer(
        text="".join(text_parts),
        parse_mode="HTML",
        reply_markup=get_playlist_manage_keyboard(),
    )


@router.message(Command("listemisil", "clearplaylist", "deleteplaylist"))
async def cmd_listemisil(message: Message) -> None:
    """
    /listemisil komutu.
    Çalma listesini tamamen siler.
    """
    user_id = message.from_user.id
    deleted = await clear_playlist(user_id)

    if deleted > 0:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                f" <b>ÇALMA LİSTEN TAMAMEN SİLİNDİ!</b>\n"
                f"🗑️ {deleted} şarkı silindi."
            ),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>ÇALMA LİSTEN ZATEN BOŞ.</b>"
            ),
            parse_mode="HTML",
        )
