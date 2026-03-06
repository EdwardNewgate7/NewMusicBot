"""
Harmony Music - Hoş Geldin Sistemi
Gruba yeni üye katıldığında otomatik karşılama mesajı gönderir.
/hosgeldin on/off ile açılıp kapatılabilir.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import ChatMemberUpdatedFilter, Command, IS_NOT_MEMBER, MEMBER
from aiogram.types import ChatMemberUpdated, Message

from database.models import get_welcome_enabled, set_welcome_enabled, upsert_group
from filters.admin import IsAdmin
from utils.emoji_ids import emoji
from config import config

router = Router(name="welcome")


@router.message(Command("hosgeldin", "welcome"), IsAdmin())
async def cmd_welcome(message: Message) -> None:
    """
    /hosgeldin [on/off] komutu.
    Grubun hoş geldin mesajını açar veya kapatır.
    """
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        current = await get_welcome_enabled(message.chat.id)
        status = "✅ AKTİF" if current else "❌ KAPALI"
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
                f" <b>HOŞ GELDİN MESAJI:</b> {status}\n\n"
                "<b>Kullanım:</b>\n"
                "├ <code>/hosgeldin on</code> — Aç\n"
                "└ <code>/hosgeldin off</code> — Kapat"
            ),
            parse_mode="HTML",
        )
        return

    arg = args[1].lower().strip()
    if arg in ("on", "aç", "ac", "aktif", "enable"):
        await set_welcome_enabled(message.chat.id, True)
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.CHECKMARK}">☑️</tg-emoji>'
                " <b>HOŞ GELDİN MESAJI AKTİF EDİLDİ.</b>\n"
                "<i>Yeni üyeler gruba katıldığında karşılanacak.</i>"
            ),
            parse_mode="HTML",
        )
    elif arg in ("off", "kapat", "pasif", "disable"):
        await set_welcome_enabled(message.chat.id, False)
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>HOŞ GELDİN MESAJI KAPATILDI.</b>"
            ),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>GEÇERSİZ PARAMETRE!</b>\n\n"
                "<b>Kullanım:</b> <code>/hosgeldin on</code> veya "
                "<code>/hosgeldin off</code>"
            ),
            parse_mode="HTML",
        )


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> MEMBER))
async def on_new_member(event: ChatMemberUpdated) -> None:
    """
    Gruba yeni üye katıldığında tetiklenir.
    Bot kendisi katıldığında log grubuna detaylı bildirim gönderir.
    """
    # Bot kendisi eklendiyse
    if event.new_chat_member.user.id == event.bot.id:
        # Botu ekleyen grup otomatik kaydet
        await upsert_group(
            chat_id=event.chat.id,
            title=event.chat.title,
            added_by=event.from_user.id if event.from_user else None,
        )
        await event.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
                " <b>HARMONY MUSIC v3.0 AKTİF!</b>\n\n"
                "Merhaba! Ben bu grubun müzik asistanıyım.\n\n"
                "🎵 <code>/oynat</code> Şarkı çal (320kbps)\n"
                "🔍 <code>/ara</code> Şarkı ara\n"
                "📝 <code>/sozler</code> Şarkı sözleri\n"
                "🔁 <code>/loop</code> Tekrar modu\n"
                "❓ <code>/yardim</code> Tüm komutlar"
            ),
            parse_mode="HTML",
        )
        
        # Log grubuna detaylı bildirim gönder
        try:
            from_user = event.from_user
            adder_name = from_user.first_name if from_user else "Bilinmeyen"
            adder_id = from_user.id if from_user else "Bilinmeyen"
            adder_mention = from_user.mention_html() if from_user else "Bilinmeyen"
            
            chat = event.chat
            chat_title = chat.title
            chat_id = chat.id
            chat_username = f"@{chat.username}" if chat.username else "Gizli/Özel"
            
            # Üye sayısını almayı dene
            try:
                member_count = await event.bot.get_chat_member_count(chat_id)
            except:
                member_count = "Bilinmiyor"
            
            await event.bot.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"🟢 <b>BOT GRUBA EKLENDİ!</b>\n\n"
                    f"<b>👥 Grup:</b> <code>{chat_title}</code>\n"
                    f"<b>🆔 ID:</b> <code>{chat_id}</code>\n"
                    f"<b>🔗 Link:</b> {chat_username}\n"
                    f"<b>👤 Ekleyen:</b> {adder_mention} (<code>{adder_id}</code>)\n"
                    f"<b>📊 Üye Sayısı:</b> <code>{member_count}</code>"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            import logging
            logging.getLogger("WelcomeLog").error(f"Eklendi logu gönderilemedi: {e}")
            
        return

    # Hoş geldin aktif mi kontrol et
    if not await get_welcome_enabled(event.chat.id):
        return


@router.chat_member(ChatMemberUpdatedFilter(MEMBER >> IS_NOT_MEMBER))
async def on_bot_removed(event: ChatMemberUpdated) -> None:
    """
    Bot gruptan çıkarıldığında veya grup/kanal silindiğinde tetiklenir.
    Log grubuna bildirim gönderir.
    """
    if event.new_chat_member.user.id == event.bot.id:
        try:
            chat = event.chat
            chat_title = chat.title
            chat_id = chat.id
            
            remover = event.from_user
            remover_name = remover.first_name if remover else "Bilinmeyen"
            remover_id = remover.id if remover else "Bilinmeyen"
            
            await event.bot.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"🔴 <b>BOT GRUPTAN ÇIKARILDI!</b>\n\n"
                    f"<b>👥 Grup:</b> <code>{chat_title}</code>\n"
                    f"<b>🆔 ID:</b> <code>{chat_id}</code>\n"
                    f"<b>👤 Çıkaran/Kovan:</b> {remover_name} (<code>{remover_id}</code>)\n"
                    f"<i>Bot artık bu grupta hizmet vermiyor.</i>"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            import logging
            logging.getLogger("WelcomeLog").error(f"Çıkarıldı logu gönderilemedi: {e}")

    user = event.new_chat_member.user
    name = user.first_name or "Misafir"
    chat_title = event.chat.title or "Grup"

    await event.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>HOŞ GELDİN, {name}!</b> 👋\n\n"
            f"<b>{chat_title}</b> ailesine katıldın.\n\n"
            "├ 🎵 Müzik çalmak istersen: <code>/oynat</code>\n"
            "├ 📋 Çalma listeni yönet: <code>/playlist</code>\n"
            "└ ❓ Yardım al: <code>/yardim</code>\n\n"
            "<i>İyi eğlenceler!</i> 🎶"
        ),
        parse_mode="HTML",
    )
