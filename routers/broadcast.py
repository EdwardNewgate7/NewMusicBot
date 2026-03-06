"""
Harmony Music - Duyuru/Broadcast Sistemi
Bot sahibinin tüm gruplara ve kullanıcılara mesaj göndermesi.
/duyuru komutu - sadece sahipler kullanabilir.
"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.models import get_all_chat_ids, get_all_user_ids
from filters.admin import IsOwner
from utils.emoji_ids import emoji

router = Router(name="broadcast")
logger = logging.getLogger("Broadcast")

# Aktif duyuru takibi
_broadcasting = False


@router.message(Command("duyuru", "broadcast"), IsOwner())
async def cmd_broadcast(message: Message) -> None:
    """
    /duyuru komutu (sadece sahip).
    Yanıtlanan mesajı tüm gruplara iletir.
    Seçenekler: -user (kullanıcılara da gönder)
    """
    global _broadcasting

    if not message.reply_to_message:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN DUYURU OLARAK GÖNDERİLECEK"
                " MESAJI YANITLAYIN.</b>\n\n"
                "<b>Kullanım:</b>\n"
                "├ Bir mesajı yanıtla + <code>/duyuru</code>\n"
                "└ Kullanıcılara da: <code>/duyuru -user</code>"
            ),
            parse_mode="HTML",
        )
        return

    if _broadcasting:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>BİR DUYURU ZATEN DEVAM EDİYOR!</b>\n"
                "İptal için: <code>/duyurudur</code>"
            ),
            parse_mode="HTML",
        )
        return

    msg = message.reply_to_message
    include_users = "-user" in message.text.lower()

    # Hedef listeleri oluştur
    targets = []
    groups = await get_all_chat_ids()
    targets.extend(groups)

    if include_users:
        users = await get_all_user_ids()
        targets.extend(users)

    if not targets:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>GÖNDERİLECEK HEDEF BULUNAMADI.</b>"
            ),
            parse_mode="HTML",
        )
        return

    _broadcasting = True
    status = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>DUYURU BAŞLADI!</b>\n\n"
            f"├ Gruplar: <code>{len(groups)}</code>\n"
            f"├ Kullanıcılar: <code>{len(targets) - len(groups)}</code>\n"
            f"└ Toplam: <code>{len(targets)}</code>"
        ),
        parse_mode="HTML",
    )

    success_groups = 0
    success_users = 0
    failed = 0

    for target_id in targets:
        if not _broadcasting:
            break

        try:
            await msg.forward(target_id)
            if target_id in groups:
                success_groups += 1
            else:
                success_users += 1
            await asyncio.sleep(0.15)  # Flood önleme
        except Exception as e:
            failed += 1
            logger.debug(f"Duyuru hatası ({target_id}): {e}")
            continue

    _broadcasting = False

    await status.edit_text(
        text=(
            f'<tg-emoji emoji-id="{emoji.CHECKMARK}">☑️</tg-emoji>'
            f" <b>DUYURU TAMAMLANDI!</b>\n\n"
            f"├ ✅ Gruplar: <code>{success_groups}</code>\n"
            f"├ ✅ Kullanıcılar: <code>{success_users}</code>\n"
            f"└ ❌ Başarısız: <code>{failed}</code>"
        ),
        parse_mode="HTML",
    )


@router.message(Command("duyurudur", "stop_broadcast", "cancel_broadcast"), IsOwner())
async def cmd_stop_broadcast(message: Message) -> None:
    """/duyurudur - Aktif duyuruyu durdurur."""
    global _broadcasting

    if not _broadcasting:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>AKTİF DUYURU YOK.</b>"
            ),
            parse_mode="HTML",
        )
        return

    _broadcasting = False
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.CHECKMARK}">☑️</tg-emoji>'
            " <b>DUYURU DURDURULDU.</b>"
        ),
        parse_mode="HTML",
    )
