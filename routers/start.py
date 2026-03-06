"""
Harmony Music - /start Komutu Router'ı
Kullanıcının ilk etkileşimini yönetir.
"""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import config
from utils.keyboards import get_start_inline_keyboard
from utils.texts import start_text

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    /start komutu handler'ı.

    Kullanıcıya özel emoji içeren karşılama mesajı ve
    renkli inline butonlar gönderir.
    """
    user_first_name = message.from_user.first_name or "Kullanıcı"

    # Karşılama mesajı metni (HTML + özel emojiler)
    text = start_text(user_first_name)

    # Inline klavye (style + icon_custom_emoji_id parametreleri)
    keyboard = get_start_inline_keyboard(
        bot_username=config.BOT_USERNAME,
        assistant_username=config.ASSISTANT_BOT_USERNAME.lstrip("@"),
        dev1_username=config.DEV_USERNAME,
        dev2_username=config.DEV2_USERNAME,
    )

    await message.answer(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    # Özelden ilk kez başlatıldıysa bildirim gönder (veya her startta)
    if message.chat.type == "private":
        try:
            user = message.from_user
            name = user.first_name or "Bilinmeyen"
            uid = user.id
            username = f"@{user.username}" if user.username else "Yok"
            
            await message.bot.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"🚀 <b>YENİ KULLANICI BOTU BAŞLATTI!</b>\n\n"
                    f"<b>Kullanıcı:</b> {name}\n"
                    f"<b>Kullanıcı ID:</b> <code>{uid}</code>\n"
                    f"<b>Kullanıcı Adı:</b> {username}"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            import logging
            logging.getLogger("StartLog").error(f"Kullanıcı start logu gönderilemedi: {e}")
