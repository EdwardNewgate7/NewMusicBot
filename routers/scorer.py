"""
Harmony Music - Mesaj Skor & Sıralama Sistemi
Gruptaki en aktif üyeleri takip eder ve sıralama gösterir.
/top, /benimskor, /grupistatistik, /skoryardım komutları.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.models import (
    get_group_message_stats,
    get_leaderboard,
    get_user_message_stats,
    get_user_rank,
)
from filters.admin import IsGroup
from utils.emoji_ids import emoji

router = Router(name="scorer")


# ── Sıralama Rozeti ───────────────────────────────────────────
def _rank_badge(rank: int) -> str:
    if rank == 1:
        return "🥇"
    if rank == 2:
        return "🥈"
    if rank == 3:
        return "🥉"
    if rank <= 5:
        return "🏅"
    return "⬜"


# ── Aktivite Seviyesi ─────────────────────────────────────────
def _activity_level(total: int) -> str:
    if total > 1000:
        return "🔥 Çok Aktif"
    if total > 500:
        return "⚡ Aktif"
    if total > 100:
        return "✨ Orta"
    if total > 50:
        return "💫 Az Aktif"
    return "💤 Düşük"


# ── Sıralama Butonları ────────────────────────────────────────
def _top_keyboard(current: str) -> InlineKeyboardMarkup:
    styles = {
        "daily": "primary",
        "weekly": "primary",
        "monthly": "success",
        "alltime": "success",
    }
    buttons = {
        "daily": ("📅 Günlük", "top_daily"),
        "weekly": ("📆 Haftalık", "top_weekly"),
        "monthly": ("🗓️ Aylık", "top_monthly"),
        "alltime": ("📊 Toplam", "top_alltime"),
    }
    row = []
    for key, (label, cb) in buttons.items():
        if key != current:
            row.append(InlineKeyboardButton(
                text=label,
                callback_data=cb,
                icon_custom_emoji_id=emoji.STAT_CHART,
                style=styles.get(key, "primary"),
            ))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            row[:2],
            row[2:] + [
                InlineKeyboardButton(
                    text="KAPAT",
                    callback_data="top_close",
                    icon_custom_emoji_id=emoji.STOP,
                    style="danger",
                ),
            ],
        ]
    )



# ── Periyot Başlıkları ────────────────────────────────────────
PERIOD_HEADERS = {
    "daily": ("Günlük", "BUGÜN"),
    "weekly": ("Haftalık", "BU HAFTA"),
    "monthly": ("Aylık", "BU AY"),
    "alltime": ("Tüm Zamanlar", "TÜM ZAMANLARDA"),
}


async def _build_leaderboard_text(
    chat_id: int,
    period: str,
    requester_id: int,
    requester_name: str,
    bot,
) -> str:
    """Liderlik tablosu metnini oluşturur."""
    _, header = PERIOD_HEADERS.get(period, ("Günlük", "BUGÜN"))
    results = await get_leaderboard(chat_id, period, limit=20)

    text = (
        f'<tg-emoji emoji-id="{emoji.STAT_CHART}">📊</tg-emoji>'
        f" <b>{header} EN AKTİF ÜYELER:</b>\n\n"
    )

    if not results:
        text += "😴 <i>Henüz kimse mesaj göndermedi.</i>"
        return text

    requester_count = 0
    lines = []
    for i, row in enumerate(results, 1):
        uid = row["user_id"]
        count = row["count"]

        if uid == requester_id:
            requester_count = count

        # Kullanıcı adını almaya çalış
        try:
            chat_member = await bot.get_chat_member(chat_id, uid)
            name = chat_member.user.first_name or "Bilinmeyen"
        except Exception:
            name = "Bilinmeyen"

        badge = _rank_badge(i)
        lines.append(f"{badge} <b>{i}.</b> {name} : <code>{count}</code>")

    text += "\n".join(lines)

    # Talep edenin sırası
    if requester_count == 0:
        rank = await get_user_rank(chat_id, period, requester_id)
        if rank > 0:
            stats = await get_user_message_stats(requester_id, chat_id)
            period_key = period if period != "alltime" else "alltime"
            requester_count = stats.get(period_key, 0)
    else:
        rank = await get_user_rank(chat_id, period, requester_id)

    text += f"\n\n👤 <b>Sen ({requester_name}):</b> {requester_count} mesaj"
    if rank > 0:
        text += f" (#{rank})"

    return text


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                       /top & /skor
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("top", "skor", "leaderboard"), IsGroup())
async def cmd_top(message: Message) -> None:
    """/top - Günlük sıralama (varsayılan)."""
    text = await _build_leaderboard_text(
        chat_id=message.chat.id,
        period="daily",
        requester_id=message.from_user.id,
        requester_name=message.from_user.first_name or "Kullanıcı",
        bot=message.bot,
    )
    await message.answer(
        text=text,
        parse_mode="HTML",
        reply_markup=_top_keyboard("daily"),
    )


@router.callback_query(F.data.startswith("top_"))
async def cb_top(callback: CallbackQuery) -> None:
    """Sıralama periyot değişimi callback'i."""
    action = callback.data.replace("top_", "")

    if action == "close":
        await callback.message.delete()
        await callback.answer()
        return

    if action not in PERIOD_HEADERS:
        await callback.answer("Geçersiz periyot!", show_alert=True)
        return

    text = await _build_leaderboard_text(
        chat_id=callback.message.chat.id,
        period=action,
        requester_id=callback.from_user.id,
        requester_name=callback.from_user.first_name or "Kullanıcı",
        bot=callback.bot,
    )

    try:
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=_top_keyboard(action),
        )
    except Exception:
        pass
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                    /benimskor & /mystats
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("benimskor", "mystats"), IsGroup())
async def cmd_mystats(message: Message) -> None:
    """/benimskor - Kişisel mesaj istatistiklerin."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    name = message.from_user.first_name or "Kullanıcı"

    stats = await get_user_message_stats(user_id, chat_id)
    d_rank = await get_user_rank(chat_id, "daily", user_id)
    w_rank = await get_user_rank(chat_id, "weekly", user_id)
    m_rank = await get_user_rank(chat_id, "monthly", user_id)

    total = stats["daily"] + stats["weekly"] + stats["monthly"]
    level = _activity_level(total)

    text = (
        f'<tg-emoji emoji-id="{emoji.STAT_CHART}">📊</tg-emoji>'
        f" <b>{name} — MESAJ İSTATİSTİKLERİ</b>\n\n"
        f"📅 <b>Günlük:</b> <code>{stats['daily']}</code> mesaj"
    )
    if d_rank > 0:
        text += f" (#{d_rank})"
    text += (
        f"\n📆 <b>Haftalık:</b> <code>{stats['weekly']}</code> mesaj"
    )
    if w_rank > 0:
        text += f" (#{w_rank})"
    text += (
        f"\n🗓️ <b>Aylık:</b> <code>{stats['monthly']}</code> mesaj"
    )
    if m_rank > 0:
        text += f" (#{m_rank})"
    text += (
        f"\n📊 <b>Toplam:</b> <code>{stats['alltime']}</code> mesaj"
        f"\n\n🏆 <b>Aktivite Seviyesi:</b> {level}"
    )

    await message.answer(text=text, parse_mode="HTML")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              /grupistatistik & /groupstats
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("grupistatistik", "groupstats"), IsGroup())
async def cmd_group_stats(message: Message) -> None:
    """/grupistatistik - Grubun genel mesaj istatistikleri."""
    chat_id = message.chat.id
    stats = await get_group_message_stats(chat_id)
    chat_title = message.chat.title or "Grup"

    total_activity = stats["daily_total"] + stats["weekly_total"] + stats["monthly_total"]
    if total_activity > 5000:
        level = "🔥 Çok Yüksek"
    elif total_activity > 2000:
        level = "⚡ Yüksek"
    elif total_activity > 1000:
        level = "✨ Orta"
    elif total_activity > 500:
        level = "💫 Düşük"
    else:
        level = "💤 Çok Düşük"

    text = (
        f'<tg-emoji emoji-id="{emoji.STAT_CHART}">📊</tg-emoji>'
        f" <b>{chat_title.upper()} İSTATİSTİKLERİ</b>\n\n"
        f"<b>📅 Günlük (Bugün)</b>\n"
        f"├ Aktif Kullanıcı: <code>{stats['daily_users']}</code>\n"
        f"├ Toplam Mesaj: <code>{stats['daily_total']}</code>\n\n"
        f"<b>📆 Haftalık (Bu Hafta)</b>\n"
        f"├ Aktif Kullanıcı: <code>{stats['weekly_users']}</code>\n"
        f"├ Toplam Mesaj: <code>{stats['weekly_total']}</code>\n\n"
        f"<b>🗓️ Aylık (Bu Ay)</b>\n"
        f"├ Aktif Kullanıcı: <code>{stats['monthly_users']}</code>\n"
        f"├ Toplam Mesaj: <code>{stats['monthly_total']}</code>\n\n"
        f"🏆 <b>Genel Aktivite Seviyesi:</b> {level}"
    )

    await message.answer(text=text, parse_mode="HTML")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                      /skoryardım
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("skoryardim", "scorehelp"))
async def cmd_score_help(message: Message) -> None:
    """/skoryardım - Skor sistemi hakkında yardım."""
    text = (
        f'<tg-emoji emoji-id="{emoji.STAT_CHART}">📊</tg-emoji>'
        " <b>MESAJ SKOR SİSTEMİ YARDIM</b>\n\n"
        "<b>Komutlar:</b>\n"
        "├ <code>/top</code> — Günlük sıralama\n"
        "├ <code>/benimskor</code> — Kişisel istatistiklerin\n"
        "├ <code>/grupistatistik</code> — Grup istatistikleri\n"
        "└ <code>/skoryardim</code> — Bu yardım mesajı\n\n"
        "<b>Sıralama Rozetleri:</b>\n"
        "🥇 <b>1.</b> — Altın madalya\n"
        "🥈 <b>2.</b> — Gümüş madalya\n"
        "🥉 <b>3.</b> — Bronz madalya\n"
        "🏅 <b>4-5.</b> — Başarı rozeti\n"
        "⬜ <b>6+</b> — Katılım rozeti\n\n"
        "<b>Aktivite Seviyeleri:</b>\n"
        "🔥 1000+ mesaj → Çok Aktif\n"
        "⚡ 500+ mesaj → Aktif\n"
        "✨ 100+ mesaj → Orta\n"
        "💫 50+ mesaj → Az Aktif\n"
        "💤 50- mesaj → Düşük\n\n"
        "<i>Her mesajınız puan kazandırır!</"
        "i>"
    )
    await message.answer(text=text, parse_mode="HTML")
