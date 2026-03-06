"""
╔══════════════════════════════════════════════════════════════╗
║     🎵 Harmony Music - Eğlence Komutları v3.0             ║
║     Truth/Dare, Zar, Yazı/Tura, Seçim - Renkli Butonlarla  ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import random

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from utils.emoji_ids import emoji

router = Router(name="fun")

TRUTH_API = "https://api.truthordarebot.xyz/v1/truth"
DARE_API = "https://api.truthordarebot.xyz/v1/dare"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                TRUTH OR DARE (DOĞRULUK/CESARET)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _truth_dare_keyboard() -> InlineKeyboardMarkup:
    """Doğruluk & Cesaret oyun klavyesi (renkli)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="DOĞRULUK",
                    callback_data="truth_new",
                    icon_custom_emoji_id=emoji.SPARKLE,
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="CESARET",
                    callback_data="dare_new",
                    icon_custom_emoji_id=emoji.FIRE,
                    style="danger",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="KAPAT",
                    callback_data="fun_close",
                    icon_custom_emoji_id=emoji.STOP,
                    style="danger",
                ),
            ],
        ]
    )


@router.message(Command("dogru", "truth"))
async def cmd_truth(message: Message) -> None:
    """/dogru - Doğruluk sorusu getirir."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                TRUTH_API, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    question = data.get("question", "Soru bulunamadı.")
                    await message.answer(
                        text=(
                            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
                            " <b>DOĞRULUK:</b>\n\n"
                            f"❓ <i>{question}</i>"
                        ),
                        parse_mode="HTML",
                        reply_markup=_truth_dare_keyboard(),
                    )
                else:
                    await message.answer(
                        text=(
                            f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                            " <b>SORU GETİRİLEMEDİ.</b>"
                        ),
                        parse_mode="HTML",
                    )
    except Exception:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>BAĞLANTI HATASI.</b>"
            ),
            parse_mode="HTML",
        )


@router.message(Command("cesaret", "dare"))
async def cmd_dare(message: Message) -> None:
    """/cesaret - Cesaret görevi getirir."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                DARE_API, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    question = data.get("question", "Görev bulunamadı.")
                    await message.answer(
                        text=(
                            f'<tg-emoji emoji-id="{emoji.FIRE}">🔥</tg-emoji>'
                            " <b>CESARET:</b>\n\n"
                            f"🔥 <i>{question}</i>"
                        ),
                        parse_mode="HTML",
                        reply_markup=_truth_dare_keyboard(),
                    )
                else:
                    await message.answer(
                        text=(
                            f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                            " <b>GÖREV GETİRİLEMEDİ.</b>"
                        ),
                        parse_mode="HTML",
                    )
    except Exception:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>BAĞLANTI HATASI.</b>"
            ),
            parse_mode="HTML",
        )


# ── Callback: Yeni soru / görev ────────────────────────────────


@router.callback_query(F.data == "truth_new")
async def cb_truth_new(callback: CallbackQuery) -> None:
    """Yeni doğruluk sorusu."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                TRUTH_API, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    question = data.get("question", "Soru bulunamadı.")
                    await callback.message.edit_text(
                        text=(
                            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
                            " <b>DOĞRULUK:</b>\n\n"
                            f"❓ <i>{question}</i>"
                        ),
                        parse_mode="HTML",
                        reply_markup=_truth_dare_keyboard(),
                    )
                    await callback.answer()
                else:
                    await callback.answer(
                        "❌ Soru getirilemedi!", show_alert=True
                    )
    except Exception:
        await callback.answer("❌ Bağlantı hatası!", show_alert=True)


@router.callback_query(F.data == "dare_new")
async def cb_dare_new(callback: CallbackQuery) -> None:
    """Yeni cesaret görevi."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                DARE_API, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    question = data.get("question", "Görev bulunamadı.")
                    await callback.message.edit_text(
                        text=(
                            f'<tg-emoji emoji-id="{emoji.FIRE}">🔥</tg-emoji>'
                            " <b>CESARET:</b>\n\n"
                            f"🔥 <i>{question}</i>"
                        ),
                        parse_mode="HTML",
                        reply_markup=_truth_dare_keyboard(),
                    )
                    await callback.answer()
                else:
                    await callback.answer(
                        "❌ Görev getirilemedi!", show_alert=True
                    )
    except Exception:
        await callback.answer("❌ Bağlantı hatası!", show_alert=True)


@router.callback_query(F.data == "fun_close")
async def cb_fun_close(callback: CallbackQuery) -> None:
    """Eğlence mesajını kapatır."""
    await callback.message.delete()
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                        ZAR & YAZITIRA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _dice_keyboard() -> InlineKeyboardMarkup:
    """Zar oyun butonları (renkli)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="TEKRAR AT",
                    callback_data="dice_reroll",
                    icon_custom_emoji_id=emoji.SPARKLE,
                    style="success",
                ),
                InlineKeyboardButton(
                    text="YAZI/TURA",
                    callback_data="flip_new",
                    icon_custom_emoji_id=emoji.STAR,
                    style="primary",
                ),
            ],
        ]
    )


@router.message(Command("zar", "dice", "roll"))
async def cmd_dice(message: Message) -> None:
    """/zar - Zar atar."""
    result = random.randint(1, 6)
    dice_emojis = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>ZAR ATILDI!</b>\n\n"
            f"🎲 {dice_emojis[result - 1]}  →  <b>{result}</b>"
        ),
        parse_mode="HTML",
        reply_markup=_dice_keyboard(),
    )


@router.message(Command("yazitura", "flip", "coin"))
async def cmd_flip(message: Message) -> None:
    """/yazitura - Yazı tura atar."""
    result = random.choice(["YAZI", "TURA"])
    coin = "📝" if result == "YAZI" else "🪙"
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>YAZI / TURA</b>\n\n"
            f"{coin}  →  <b>{result}!</b>"
        ),
        parse_mode="HTML",
        reply_markup=_dice_keyboard(),
    )


@router.callback_query(F.data == "dice_reroll")
async def cb_dice_reroll(callback: CallbackQuery) -> None:
    """Tekrar zar at."""
    result = random.randint(1, 6)
    dice_emojis = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    await callback.message.edit_text(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>ZAR ATILDI!</b>\n\n"
            f"🎲 {dice_emojis[result - 1]}  →  <b>{result}</b>"
        ),
        parse_mode="HTML",
        reply_markup=_dice_keyboard(),
    )
    await callback.answer(f"🎲 {result} geldi!")


@router.callback_query(F.data == "flip_new")
async def cb_flip_new(callback: CallbackQuery) -> None:
    """Tekrar yazı/tura at."""
    result = random.choice(["YAZI", "TURA"])
    coin = "📝" if result == "YAZI" else "🪙"
    await callback.message.edit_text(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>YAZI / TURA</b>\n\n"
            f"{coin}  →  <b>{result}!</b>"
        ),
        parse_mode="HTML",
        reply_markup=_dice_keyboard(),
    )
    await callback.answer(f"{coin} {result}!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     SEÇİM & SAYI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("sec", "choose", "pick"))
async def cmd_choose(message: Message) -> None:
    """/sec seçenek1, seçenek2, ... - Rastgele seçim yapar."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>SEÇENEKLER GEREKLİ!</b>\n\n"
                "<b>Kullanım:</b> <code>/sec pizza, hamburger, döner</code>"
            ),
            parse_mode="HTML",
        )
        return

    options = [o.strip() for o in args[1].split(",") if o.strip()]
    if len(options) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>EN AZ 2 SEÇENEK GEREKLİ!</b>"
            ),
            parse_mode="HTML",
        )
        return

    chosen = random.choice(options)
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>RASTGELE SEÇİM:</b>\n\n"
            f"🎯  →  <b>{chosen}</b>"
        ),
        parse_mode="HTML",
    )


@router.message(Command("sayi", "random", "number"))
async def cmd_random_number(message: Message) -> None:
    """/sayi [min] [max] - Rastgele sayı."""
    args = message.text.split()
    try:
        if len(args) == 3:
            min_val, max_val = int(args[1]), int(args[2])
        elif len(args) == 2:
            min_val, max_val = 1, int(args[1])
        else:
            min_val, max_val = 1, 100
    except ValueError:
        min_val, max_val = 1, 100

    result = random.randint(min_val, max_val)
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>RASTGELE SAYI ({min_val}-{max_val}):</b>\n\n"
            f"🔢  →  <b>{result}</b>"
        ),
        parse_mode="HTML",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     SİHİRLİ 8 TOP & AŞK METRE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("sor", "ask", "8ball"))
async def cmd_ask(message: Message) -> None:
    """/sor [SORU] - Sihirli top soruyu yanıtlar."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>BANA BİR SORU SORMALISIN!</b>\n\n"
                "<b>Kullanım:</b> <code>/sor Yarın hava güzel olacak mı?</code>"
            ),
            parse_mode="HTML",
        )
        return

    answers = [
        "Kesinlikle evet. 🌟",
        "Kuşkusuz öyle. ✨",
        "Şüphesiz. 💯",
        "Evet, kesinlikle. ✅",
        "Buna güvenebilirsin. 🫂",
        "Gördüğüm kadarıyla evet. 👀",
        "Büyük ihtimalle. 📈",
        "İyi görünüyor. 🔮",
        "Evet. 👍",
        "Belirtiler evet diyor. 🎯",
        "Şu an cevap veremiyorum, tekrar dene. 🔄",
        "Daha sonra tekrar sor. ⏳",
        "Şimdi söylemesem daha iyi. 🤐",
        "Şu an tahmin edemiyorum. 🤷‍♂️",
        "Odaklan ve tekrar sor. 🧘‍♂️",
        "Buna bel bağlama. 📉",
        "Benim cevabım hayır. 👎",
        "Kaynaklarım hayır diyor. ❌",
        "Pek iyi görünmüyor. 🌑",
        "Çok şüpheli. 🤔"
    ]
    
    question = args[1]
    chosen_answer = random.choice(answers)
    
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>SİHİRLİ KÜRE CEVAPLIYOR:</b>\n\n"
            f"❓ <b>Soru:</b> {question}\n"
            f"🔮 <b>Cevap:</b> <b>{chosen_answer}</b>"
        ),
        parse_mode="HTML",
    )


@router.message(Command("askmetre", "love", "ask", "ship"))
async def cmd_love(message: Message) -> None:
    """/askmetre [YANITLA] - İki kişi arasındaki aşk uyumunu ölçer."""
    if not message.reply_to_message:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN AŞK UYUMUNU ÖLÇMEK İSTEDİĞİNİZ KİŞİYİ YANITLAYIN!</b>\n\n"
                "<b>Kullanım:</b> Bir mesaja yanıt olarak <code>/askmetre</code> yazın."
            ),
            parse_mode="HTML",
        )
        return

    user1 = message.from_user.first_name
    user2 = message.reply_to_message.from_user.first_name
    
    if message.from_user.id == message.reply_to_message.from_user.id:
        percent = 100
        comment = "Kendini bu kadar çok sevmen harika! 🥰"
    else:
        # Aynı iki kişi için her gün aynı sonucu vermesi veya rastgele mi olması?
        # Biz direkt rastgele yapalım, eğlence botu.
        percent = random.randint(0, 100)
        
        if percent < 20:
            comment = "Zorla güzellik olmaz... Biraz uzak durun. 🧊"
        elif percent < 40:
            comment = "Sadece arkadaş olarak daha iyisiniz. 🫂"
        elif percent < 60:
            comment = "Fena değil, aranızda bir şeyler olabilir. 🧐"
        elif percent < 80:
            comment = "Çok iyi bir çiftsiniz! Kıpır kıpır! 🔥"
        elif percent < 95:
            comment = "Mükemmel uyum! Düğün ne zaman? 💍"
        else:
            comment = "SİZ RUH EŞİSİNİZ! KADER SİZİ BİR ARAYA GETİRDİ! ❤️‍🔥"

    bar_len = 10
    filled = int(bar_len * percent / 100)
    bar = "💖" * filled + "🤍" * (bar_len - filled)
    
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>AŞK METRE SONUÇLARI</b>\n\n"
            f"👩‍❤️‍👨 <b>{user1}</b>  x  <b>{user2}</b>\n\n"
            f"💘 <b>Uyumluluk:</b> %{percent}\n"
            f"[{bar}]\n\n"
            f"📝 <b>Yorum:</b> {comment}"
        ),
        parse_mode="HTML",
    )
