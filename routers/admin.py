"""
╔══════════════════════════════════════════════════════════════╗
║  🎵 Harmony Music - Admin, Genel & Gelişmiş Komutlar v3.0 ║
║  Yönetici, etiketleme, istatistik, geçmiş, favori, radyo   ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import config
from database.models import (
    add_listen_history,
    ban_user,
    get_bot_stat,
    get_group_count,
    get_listen_history,
    get_soulmate,
    get_total_user_count,
    get_top_songs,
    get_user_stats,
    increment_bot_stat,
    remove_soulmate,
    set_soulmate,
    unban_user,
)
from filters.admin import IsAdmin, IsOwner
from services.music import (
    format_duration,
    format_file_size,
    format_views,
    get_download_dir_size,
    get_download_file_count,
    search_youtube,
    validate_cookie_file,
)
from services.queue import queue_manager
from utils.emoji_ids import emoji
from utils.keyboards import (
    get_admin_panel_keyboard,
    get_settings_keyboard,
    get_yarisma_keyboard,
)

router = Router(name="admin")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#           KONTROL / AYAR KOMUTLARI (YÖNETİCİLER)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("ayarlar", "settings", "config", "setup"))
async def cmd_ayarlar(message: Message) -> None:
    """
    /ayarlar komutu.
    Grup ayarları panelini açar (yöneticiler için).
    """
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.GEAR}">⚙️</tg-emoji>'
            " <b>GRUP AYARLARI:</b>\n\n"
            "Aşağıdaki butonlardan ayarları yönetebilirsiniz."
        ),
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(),
    )


@router.message(Command("zamanla", "timer", "schedule", "time"))
async def cmd_zamanla(message: Message) -> None:
    """
    /zamanla komutu.
    Durdurma süresini belirler.
    """
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.TIMER}">⏱️</tg-emoji>'
            " <b>ZAMANLAYICI AYARLARI:</b>\n\n"
            "├ SÜRE BİTİNCE SESLİ KAPATILSIN MI SEÇ,\n"
            "└ DURDURMA SÜRESİNİ BELİRLE.\n\n"
            "<b>Kullanım:</b> <code>/zamanla 30</code> "
            "(30 dakika sonra durdur)"
        ),
        parse_mode="HTML",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#               ETİKETLEME KOMUTLARI (/tag, /atag, /davet)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# Global etiketleme kontrolü (İptal edilebilmesi için)
active_taggings = {}

@router.message(Command("tag", "mention", "call"))
async def cmd_tag(message: Message) -> None:
    """/tag [MESAJ/YANITLA] - Tüm grup üyelerini etiketler."""
    if message.chat.type == "private":
        await message.answer("❌ Bu komut sadece gruplarda kullanılabilir.")
        return

    chat_id = message.chat.id
    if chat_id in active_taggings:
        await message.answer("⚠️ Bu grupta zaten aktif bir etiketleme var. Durdurmak için: /iptal")
        return

    from services.userbot import assistant
    if not assistant.is_started:
        await message.answer("⚠️ Asistan aktif değil, bu özellik şu an kullanılamıyor.")
        return

    args = message.text.split(maxsplit=1)
    tag_msg = args[1] if len(args) > 1 else "📣 Dikkat!"
    
    # Yanıtlanan mesaj varsa ona yönlendir
    reply_to = message.reply_to_message.message_id if message.reply_to_message else message.message_id

    await message.answer(
        text=f"📣 <b>ETİKETLEME BAŞLADI...</b>\n\n<i>Mesaj: {tag_msg}</i>",
        parse_mode="HTML"
    )

    active_taggings[chat_id] = True
    
    try:
        members = await assistant.get_members(chat_id, limit=200)
        if not members:
            await message.answer("❌ Üye listesi alınamadı. Asistan grupta yetkili olmayabilir.")
            return

        batch_size = 5
        for i in range(0, len(members), batch_size):
            if chat_id not in active_taggings:
                break # İptal edildi
            
            batch = members[i:i + batch_size]
            mentions = []
            for m in batch:
                name = m.first_name or "Üye"
                mentions.append(f"<a href=\"tg://user?id={m.id}\">{name}</a>")
            
            mention_text = f"{tag_msg}\n\n" + " • ".join(mentions)
            await message.answer(text=mention_text, parse_mode="HTML", reply_to_message_id=reply_to)
            await asyncio.sleep(3) # Telegram flood koruması

        await message.answer("✅ Etiketleme tamamlandı.")
    except Exception as e:
        logger.error(f"Tagging error: {e}")
        await message.answer(f"❌ Hata oluştu: {str(e)[:50]}")
    finally:
        active_taggings.pop(chat_id, None)


@router.message(Command("atag", "adminmention", "mentionadmins"))
async def cmd_atag(message: Message) -> None:
    """/atag [MESAJ/YANITLA] - Sadece yöneticileri etiketler."""
    admins = await message.chat.get_administrators()
    
    args = message.text.split(maxsplit=1)
    tag_msg = args[1] if len(args) > 1 else "🏷️ Yöneticiler buraya!"

    mentions = []
    for admin in admins:
        if not admin.user.is_bot:
            name = admin.user.first_name or "Yönetici"
            mentions.append(f"<a href=\"tg://user?id={admin.user.id}\">{name}</a>")
    
    text = f"<b>{tag_msg}</b>\n\n" + " • ".join(mentions)
    await message.answer(text=text, parse_mode="HTML")


@router.message(Command("davet", "invite", "summon"))
async def cmd_davet(message: Message) -> None:
    """/davet - Kişileri dinlemeye/izlemeye çağırır."""
    q = queue_manager.get(message.chat.id)
    if not q.current:
        await message.answer("⚠️ Şu an bir şey çalmıyor, kimseyi davet edemem.")
        return
        
    status = "İZLEMEYE" if q.current.song.quality and "p" in q.current.song.quality else "DİNLEMEYE"
    title = q.current.song.title
    
    # /tag mantığıyla davet et
    message.text = f"/tag {status} GELİN: {title}"
    await cmd_tag(message)


@router.message(Command("iptal", "cancel", "stop_tag", "abort", "son", "bitir"))
async def cmd_iptal(message: Message) -> None:
    """/iptal - Aktif etiketleme işlemini iptal eder."""
    chat_id = message.chat.id
    if chat_id in active_taggings:
        active_taggings.pop(chat_id)
        await message.answer("✅ <b>ETİKETLEME İPTAL EDİLDİ.</b>", parse_mode="HTML")
    else:
        # Eğer müzik çalıyorsa müziği de kapatsın (kullanıcı 'bitir' diyebiliyor)
        from routers.music import cmd_son
        await cmd_son(message)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              DİĞER KOMUTLAR (/bul, /oneri, /yarisma, vb.)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("bul", "find", "search_song"))
async def cmd_bul(message: Message) -> None:
    """/bul [SÖZ/VİDEO] - Sözlerden şarkıyı bulur."""
    args = message.text.split(maxsplit=1)

    if len(args) < 2 and not message.reply_to_message:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN ŞARKI SÖZÜ YAZIN VEYA BİR VİDEOYU "
                "YANITLAYIN.</b>\n\n"
                "<b>Kullanım:</b> <code>/bul şarkı sözü</code>"
            ),
            parse_mode="HTML",
        )
        return

    query = args[1] if len(args) > 1 else "yanıtlanan video"

    status_msg = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SEARCH}">🔍</tg-emoji>'
            f" <b>ARANIYOR:</b> <code>{query[:50]}</code>\n\n"
            "<i>Lütfen bekleyin...</i>"
        ),
        parse_mode="HTML",
    )

    # YouTube'da ara
    results = await search_youtube(query, max_results=3)

    if not results:
        await status_msg.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>SONUÇ BULUNAMADI.</b>"
            ),
            parse_mode="HTML",
        )
        return

    text_parts = [
        f'<tg-emoji emoji-id="{emoji.SEARCH}">🔍</tg-emoji>'
        f' <b>BULUNAN ŞARKILAR:</b> <code>{query[:40]}</code>\n\n'
    ]

    keyboard_rows = []
    for i, song in enumerate(results, 1):
        dur = format_duration(song.duration)
        artist = song.artist or song.channel or "Bilinmeyen"
        text_parts.append(
            f"<b>{i}.</b> {song.title}\n"
            f"   👤 {artist} • ⏱ {dur}\n\n"
        )
        keyboard_rows.append([
            InlineKeyboardButton(
                text=f"{i}. OYNAT",
                callback_data=f"splay_{song.video_id}",
                icon_custom_emoji_id=emoji.PLAY,
                style="success",
            ),
            InlineKeyboardButton(
                text=f"{i}. İNDİR",
                callback_data=f"sdl_{song.video_id}",
                icon_custom_emoji_id=emoji.HEART_DOWNLOAD,
                style="primary",
            ),
        ])

    await status_msg.edit_text(
        text="".join(text_parts),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows),
    )


@router.message(Command("oneri", "recommend", "suggest", "trending_yt"))
async def cmd_oneri(message: Message) -> None:
    """/oneri - Trend müzik önerileri."""
    status_msg = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.FIRE}">🔥</tg-emoji>'
            " <b>TREND LİSTESİ YÜKLENIYOR...</b>\n\n"
            "<i>Lütfen bekleyin...</i>"
        ),
        parse_mode="HTML",
    )

    results = await search_youtube("trending müzik 2024", max_results=5)

    if not results:
        await status_msg.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>TREND LİSTESİ YÜKLENEMEDİ.</b>"
            ),
            parse_mode="HTML",
        )
        return

    text_parts = [
        f'<tg-emoji emoji-id="{emoji.FIRE}">🔥</tg-emoji>'
        " <b>TREND MÜZİK ÖNERİLERİ:</b>\n\n"
    ]

    keyboard_rows = []
    for i, song in enumerate(results, 1):
        dur = format_duration(song.duration)
        text_parts.append(f"<b>{i}.</b> {song.title} [{dur}]\n")
        keyboard_rows.append([
            InlineKeyboardButton(
                text=f"{i}. OYNAT",
                callback_data=f"splay_{song.video_id}",
                icon_custom_emoji_id=emoji.PLAY,
                style="success",
            ),
        ])

    text_parts.append("\n<i>Dinlemek istediğini seç:</i>")

    await status_msg.edit_text(
        text="".join(text_parts),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows),
    )


@router.message(Command("yarisma", "quiz", "contest", "game"))
async def cmd_yarisma(message: Message) -> None:
    """/yarisma - Şarkı bilme yarışması başlatır."""
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.TROPHY}">🏆</tg-emoji>'
            " <b>ŞARKI YARIŞMASI BAŞLATILIYOR!</b>\n\n"
            "├ ŞARKI DİLİ SEÇ (TÜRKÇE, İNGİLİZCE),\n"
            "├ TÜRÜ SEÇ (ARABESK, POP VB.),\n"
            "├ BOT 20SN MÜZİK KESİTLERİ ATACAK,\n"
            "└ İSİMLERİNİ BİL VE PUAN KAZAN.\n\n"
            "Lütfen dil ve tür seçin:"
        ),
        parse_mode="HTML",
        reply_markup=get_yarisma_keyboard(),
    )


@router.message(Command("hediye", "gift", "present", "send_song"))
async def cmd_hediye(message: Message) -> None:
    """/hediye - Birine şarkı hediye eder."""
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.GIFT}">🎁</tg-emoji>'
            " <b>ŞARKI HEDİYE ET:</b>\n\n"
            "├ ALICI İD VEYA KULLANICI ADI GİR,\n"
            "├ İSMİN GÖRÜNSÜN MÜ SEÇ,\n"
            "└ ŞARKI ADINI YAZ VE GÖNDER.\n\n"
            "<b>Kullanım:</b> <code>/hediye @kullanici şarkı adı</code>"
        ),
        parse_mode="HTML",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   RUH EŞİ KOMUTLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("ruhesi", "soulmate", "couple", "match"))
async def cmd_ruhesi(message: Message) -> None:
    """/ruhesi [YANITLA] - Ruh eşi eşleştirmesi."""
    if not message.reply_to_message:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN RUH EŞİN OLMAK İSTEDİĞİN KİŞİNİN "
                "MESAJINI YANITLA.</b>"
            ),
            parse_mode="HTML",
        )
        return

    target = message.reply_to_message.from_user
    if target.id == message.from_user.id:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>KENDİNLE EŞLEŞEMEZSIN!</b>"
            ),
            parse_mode="HTML",
        )
        return

    existing = await get_soulmate(message.from_user.id)
    if existing:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>ZATEN BİR RUH EŞİN VAR!</b>\n"
                "Ayrılmak için: <code>/ayril</code>"
            ),
            parse_mode="HTML",
        )
        return

    await set_soulmate(message.from_user.id, target.id)
    target_name = target.first_name or "Kullanıcı"

    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.HEART_COUPLE}">💕</tg-emoji>'
            f" <b>RUH EŞİ EŞLEŞTIRMESI:</b>\n\n"
            f"├ <b>{target_name}</b> İLE EŞLEŞTİRİLDİN!\n"
            "├ EŞİN HANGİ ŞARKIYI DİNLİYOR GÖR,\n"
            "├ HANGİ GRUPTA DİNLİYOR ÖĞREN,\n"
            "└ ŞARKI AÇTIĞINDA BİLGİ AL."
        ),
        parse_mode="HTML",
    )


@router.message(Command("ayril", "leave", "unsoul", "divorce"))
async def cmd_ayril(message: Message) -> None:
    """/ayril - Ruh eşinden ayrıl."""
    existing = await get_soulmate(message.from_user.id)
    if not existing:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>RUH EŞİN YOK!</b>"
            ),
            parse_mode="HTML",
        )
        return

    await remove_soulmate(message.from_user.id)
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.BROKEN_HEART}">💔</tg-emoji>'
            " <b>MEVCUT RUH EŞİNİZDEN AYRILDINIZ.</b>"
        ),
        parse_mode="HTML",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              İSTATİSTİK KOMUTLARI (/stat, /kart)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("stat", "stats", "performance"))
async def cmd_stat(message: Message) -> None:
    """/stat - Dinleme istatistikleri."""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Kullanıcı"

    stats = await get_user_stats(user_id)

    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.STAT_CHART}">📊</tg-emoji>'
            f" <b>{user_name.upper()} DİNLEME İSTATİSTİKLERİ:</b>\n\n"
            f"├ Toplam Dinleme: <code>{stats['total_plays']}</code>\n"
            f"├ Bugün: <code>{stats['today_plays']}</code>\n"
            f"├ Bu Hafta: <code>{stats['week_plays']}</code>\n"
            f"├ En Çok Dinlenen: <code>{stats['favorite_song']}</code>"
            f" ({stats['favorite_song_count']}x)\n"
            f"└ Favori Sanatçı: <code>{stats['favorite_artist']}</code>"
        ),
        parse_mode="HTML",
    )


@router.message(Command("kart", "card", "profile", "me", "id"))
async def cmd_kart(message: Message) -> None:
    """/kart - Gelişmiş istatistik kartı."""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Kullanıcı"
    stats = await get_user_stats(user_id)

    # Seviye hesapla
    plays = stats["total_plays"]
    if plays >= 500:
        level = "👑 EFSANE"
    elif plays >= 200:
        level = "💎 USTA"
    elif plays >= 100:
        level = "🔥 DENEYİMLİ"
    elif plays >= 50:
        level = "⚡ AKTİF"
    elif plays >= 10:
        level = "✨ BAŞLANGIÇ"
    else:
        level = "🌱 YENİ"

    await message.answer(
        text=(
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃  🪪 <b>{user_name.upper()}</b>\n"
            f"┃  {level}\n"
            "┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃\n"
            f"┃  🎵 Toplam: <code>{stats['total_plays']}</code> dinleme\n"
            f"┃  📅 Bugün: <code>{stats['today_plays']}</code>\n"
            f"┃  📊 Hafta: <code>{stats['week_plays']}</code>\n"
            f"┃  ❤️ Favori: <code>{stats['favorite_song']}</code>\n"
            f"┃  👤 Sanatçı: <code>{stats['favorite_artist']}</code>\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            " <b>HARMONY MUSIC v3.0</b>"
        ),
        parse_mode="HTML",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#        DİNLEME GEÇMİŞİ ve TREND (YENİ KOMUTLAR)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("gecmis", "history", "archive", "recent", "records"))
async def cmd_gecmis(message: Message) -> None:
    """
    /gecmis - Son dinleme geçmişini gösterir.
    Veritabanından son 10 dinlenen şarkıyı çeker.
    """
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Kullanıcı"

    history = await get_listen_history(user_id, limit=10)

    if not history:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.FOLDER}">📁</tg-emoji>'
                " <b>DİNLEME GEÇMİŞİN BOŞ!</b>\n\n"
                "Şarkı dinlemeye başla:\n"
                "<code>/oynat şarkı adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    text_parts = [
        f'<tg-emoji emoji-id="{emoji.FOLDER}">📁</tg-emoji>'
        f" <b>{user_name.upper()} - SON DİNLENENLER:</b>\n\n"
    ]

    keyboard_rows = []
    for i, entry in enumerate(history, 1):
        title = entry.get("title", "Bilinmeyen")
        artist = entry.get("artist", "")
        when = entry.get("listened_at", "")[:16]  # Tarih-saat
        duration = entry.get("duration", 0)

        artist_text = f" • 👤 {artist}" if artist else ""
        dur_text = f" [{format_duration(duration)}]" if duration else ""

        text_parts.append(
            f"<b>{i}.</b> {title}{dur_text}{artist_text}\n"
            f"   🕐 {when}\n"
        )

        # Tekrar oynat butonu
        url = entry.get("url", "")
        if url and "youtube" in url:
            from services.music import extract_video_id
            vid = extract_video_id(url)
            if vid:
                keyboard_rows.append([
                    InlineKeyboardButton(
                        text=f"{i}. TEKRAR OYNAT",
                        callback_data=f"splay_{vid}",
                        icon_custom_emoji_id=emoji.PLAY,
                        style="success",
                    ),
                ])

    await message.answer(
        text="".join(text_parts),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
        if keyboard_rows else None,
    )


@router.message(Command("trend", "trending", "popular", "top_songs"))
async def cmd_trend(message: Message) -> None:
    """
    /trend - En çok dinlenen şarkılar (botun veritabanından).
    """
    top_songs = await get_top_songs(limit=10)

    if not top_songs:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.FIRE}">🔥</tg-emoji>'
                " <b>HENÜZ YETERLİ VERİ YOK!</b>\n\n"
                "<i>Daha fazla şarkı dinlendikçe\n"
                "trend listesi oluşacak.</i>"
            ),
            parse_mode="HTML",
        )
        return

    text_parts = [
        f'<tg-emoji emoji-id="{emoji.FIRE}">🔥</tg-emoji>'
        " <b>EN ÇOK DİNLENEN ŞARKILAR:</b>\n\n"
    ]

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    for i, song in enumerate(top_songs):
        title = song.get("title", "Bilinmeyen")
        count = song.get("count", 0)
        artist = song.get("artist", "")
        medal = medals[i] if i < len(medals) else "▪️"

        artist_text = f" • {artist}" if artist else ""
        text_parts.append(
            f"{medal} <b>{title}</b>{artist_text}\n"
            f"   └ <code>{count}</code> kez dinlendi\n"
        )

    await message.answer(
        text="".join(text_parts),
        parse_mode="HTML",
    )


@router.message(Command("paylas", "share", "broadcast_song"))
async def cmd_paylas(message: Message) -> None:
    """
    /paylas - Şu an çalan şarkıyı paylaş.
    """
    q = queue_manager.get(message.chat.id)

    if not q.current:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>ŞU AN ÇALAN BİR ŞARKI YOK.</b>"
            ),
            parse_mode="HTML",
        )
        return

    song = q.current.song
    user_name = message.from_user.first_name or "Kullanıcı"

    share_text = (
        f'<tg-emoji emoji-id="{emoji.HEADPHONES}">🎧</tg-emoji>'
        f" <b>{user_name} BU ŞARKIYI DİNLİYOR:</b>\n\n"
        f"🎵 <b>{song.title}</b>\n"
        f"👤 {song.artist or 'Bilinmeyen'}\n"
        f"⏱ {format_duration(song.duration)}"
    )

    if song.url:
        share_text += f"\n🔗 {song.url}"

    share_text += (
        "\n\n<i>🎧 Harmony Music ile dinleniyor.</i>"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="OYNAT",
                    callback_data=f"splay_{song.video_id}" if song.video_id else "noop",
                    icon_custom_emoji_id=emoji.PLAY,
                    style="success",
                ),
                InlineKeyboardButton(
                    text="İNDİR",
                    callback_data=f"sdl_{song.video_id}" if song.video_id else "noop",
                    icon_custom_emoji_id=emoji.HEART_DOWNLOAD,
                    style="primary",
                ),
            ],
        ]
    )

    await message.answer(
        text=share_text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.message(Command("radyo", "radio", "stream", "live"))
async def cmd_radyo(message: Message) -> None:
    """
    /radyo - Canlı radyo akışını sesli sohbette başlatır.
    """
    radio_url = config.DEFAULT_RADIO_URL

    status_msg = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.HEADPHONES}">🎧</tg-emoji>'
            " <b>RADYO AKIŞI BAŞLATILIYOR...</b>\n\n"
            "📻 <b>Power FM</b>\n"
            "<i>Lütfen bekleyin...</i>"
        ),
        parse_mode="HTML"
    )

    from services.userbot import assistant
    if assistant.is_started:
        success = await assistant.play_audio(message.chat.id, radio_url)
        if success:
            await status_msg.edit_text(
                text=(
                    f'<tg-emoji emoji-id="{emoji.PLAY}">▶️</tg-emoji>'
                    " <b>RADYO YAYINI AKTİF!</b>\n\n"
                    "📻 <b>İstasyon:</b> Power FM\n"
                    "├ 7/24 Kesintisiz\n"
                    "└ İyi Dinlemeler ✨"
                ),
                parse_mode="HTML"
            )
        else:
            await status_msg.edit_text("❌ Radyo başlatılamadı. Sesli sohbet açık mı?")
    else:
        await status_msg.edit_text("⚠️ Asistan aktif değil.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#           SAHİP & YÖNETİCİ KOMUTLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("panel", "admin", "cp", "dashboard"))
async def cmd_panel(message: Message) -> None:
    """/panel - Yönetici paneli."""
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.CROWN}">👑</tg-emoji>'
            " <b>YÖNETİCİ PANELİ:</b>\n\n"
            "Aşağıdaki butonlardan panel işleyicilerini "
            "yönetebilirsiniz."
        ),
        parse_mode="HTML",
        reply_markup=get_admin_panel_keyboard(),
    )


@router.message(Command("uyku", "sleep", "maintenance"))
async def cmd_uyku(message: Message) -> None:
    """/uyku - Bakım modu."""
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SLEEP}">😴</tg-emoji>'
            " <b>BOT BAKIM MODUNA ALINDI.</b>\n\n"
            "└ BOTU DIŞARIYA KAPATIR, SADECE SİZ DİNLERSİNİZ."
        ),
        parse_mode="HTML",
    )


@router.message(Command("ban"), IsOwner())
async def cmd_ban(message: Message) -> None:
    """/ban [ID] - Kullanıcıyı yasaklar (sadece sahip)."""
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN YASAKLANACAK KULLANICININ ID'SİNİ YAZIN.</b>\n\n"
                "<b>Kullanım:</b> <code>/ban 123456789</code>"
            ),
            parse_mode="HTML",
        )
        return

    try:
        target_id = int(args[1].strip())
    except ValueError:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>GEÇERSİZ KULLANICI ID!</b>"
            ),
            parse_mode="HTML",
        )
        return

    await ban_user(target_id, message.from_user.id)
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.BAN}">🚫</tg-emoji>'
            f" <b>KULLANICI YASAKLANDI:</b> <code>{target_id}</code>"
        ),
        parse_mode="HTML",
    )


@router.message(Command("unban"), IsOwner())
async def cmd_unban(message: Message) -> None:
    """/unban [ID] - Yasağı kaldırır (sadece sahip)."""
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN KULLANICI ID YAZIN.</b>\n\n"
                "<b>Kullanım:</b> <code>/unban 123456789</code>"
            ),
            parse_mode="HTML",
        )
        return

    try:
        target_id = int(args[1].strip())
    except ValueError:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>GEÇERSİZ KULLANICI ID!</b>"
            ),
            parse_mode="HTML",
        )
        return

    await unban_user(target_id)
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.CHECKMARK}">☑️</tg-emoji>'
            f" <b>YASAK KALDIRILDI:</b> <code>{target_id}</code>"
        ),
        parse_mode="HTML",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     GENEL KOMUTLAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("ping", "latency"))
async def cmd_ping(message: Message) -> None:
    """/ping - Bot gecikmesi + canlı istatistikler."""
    start_time = time.monotonic()

    sent = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            " <b>PONG!</b> Ölçülüyor..."
        ),
        parse_mode="HTML",
    )

    end_time = time.monotonic()
    latency_ms = round((end_time - start_time) * 1000, 2)

    total_users = await get_total_user_count()
    total_groups = await get_group_count()
    active_players = queue_manager.get_total_playing()

    # Cookie ve cache bilgisi
    cookie_status = "✅" if config.get_cookie_path() else "❌"
    cache_size = format_file_size(get_download_dir_size())
    cache_files = get_download_file_count()

    await sent.edit_text(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>PONG!</b>\n\n"
            f"├ Gecikme: <code>{latency_ms}ms</code>\n"
            f"├ Kullanıcılar: <code>{total_users}</code>\n"
            f"├ Gruplar: <code>{total_groups}</code>\n"
            f"├ Aktif Çalan: <code>{active_players}</code>\n"
            f"├ 🍪 Cookie: {cookie_status}\n"
            f"├ 🎚 Kalite: {config.AUDIO_QUALITY}kbps\n"
            f"└ 💾 Önbellek: {cache_size} ({cache_files} dosya)"
        ),
        parse_mode="HTML",
    )


@router.message(Command("yardim", "help"))
async def cmd_yardim(message: Message) -> None:
    """/yardim - Yardım menüsü."""
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            " <b>YARDIM MENÜSÜ:</b>\n\n"
            "🎵 <b>MÜZİK:</b>\n"
            "├ <code>/oynat</code> Şarkı çal\n"
            "├ <code>/ara</code> Şarkı ara\n"
            "├ <code>/indir</code> Şarkı indir\n"
            "├ <code>/voynat</code> Video çal\n"
            "├ <code>/sozler</code> Şarkı sözleri\n"
            "├ <code>/calan</code> Şu an çalan\n"
            "└ <code>/loop</code> Tekrar modu\n\n"
            "📋 <b>LİSTE:</b>\n"
            "├ <code>/sira</code> Kuyruk\n"
            "├ <code>/karistir</code> Karıştır\n"
            "├ <code>/playlist</code> Çalma listesi\n"
            "└ <code>/gecmis</code> Dinleme geçmişi\n\n"
            "📊 <b>DİĞER:</b>\n"
            "├ <code>/stat</code> İstatistikler\n"
            "├ <code>/trend</code> Trend şarkılar\n"
            "├ <code>/radyo</code> Canlı radyo\n"
            "├ <code>/paylas</code> Şarkı paylaş\n"
            "└ <code>/kalite</code> Ses kalitesi"
        ),
        parse_mode="HTML",
    )


@router.message(Command("hakkinda", "about", "info"))
async def cmd_hakkinda(message: Message) -> None:
    """/hakkinda - Bot hakkında bilgi verir."""
    cookie_status = "✅ Aktif" if config.get_cookie_path() else "❌ Yok"

    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.CROWN}">👑</tg-emoji>'
            " <b>HARMONY MUSIC v3.0.0</b>\n\n"
            "├ <b>Sürüm:</b> 3.0.0\n"
            "├ <b>Dil:</b> Python 3.12+\n"
            "├ <b>Framework:</b> aiogram 3.25+\n"
            "├ <b>İndirici:</b> yt-dlp\n"
            "├ <b>Veritabanı:</b> SQLite (async)\n"
            "├ <b>Amaç:</b> Telegram'da müzik çalma\n"
            "├ <b>Durum:</b> Aktif ✅\n\n"
            "<b>━━ v3.0 ÖZELLİKLER ━━</b>\n"
            f"├ 🍪 Cookie.txt: {cookie_status}\n"
            f"├ 🎚 Kalite: {config.AUDIO_QUALITY}kbps\n"
            f"├ 📀 Format: {config.AUDIO_FORMAT.upper()}\n"
            f"├ 🎬 Video: {config.VIDEO_QUALITY}p\n"
            "├ 📝 Şarkı Sözleri\n"
            "├ 🔁 Loop / Karıştır\n"
            "├ 📻 Canlı Radyo\n"
            "├ 🔥 Trend Listesi\n"
            "├ 📋 Dinleme Geçmişi\n"
            "└ 🎵 SoundCloud Desteği"
        ),
        parse_mode="HTML",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     SABİTLEME KOMUTLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("pin", "sabitle"), IsAdmin())
async def cmd_pin(message: Message) -> None:
    """/pin - Yanıtlanan mesajı sabitler."""
    if not message.reply_to_message:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>SABİTLENECEK MESAJI YANITLAYIN!</b>"
            ),
            parse_mode="HTML",
        )
        return

    try:
        await message.chat.pin_message(
            message_id=message.reply_to_message.message_id,
            disable_notification=False
        )
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.CHECKMARK}">☑️</tg-emoji>'
                " <b>MESAJ SABİTLENDİ.</b>"
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(f"❌ Sabitleme başarısız: Yetkim yok veya bir hata oluştu. ({str(e)[:50]})")


@router.message(Command("unpin", "kaldir"), IsAdmin())
async def cmd_unpin(message: Message) -> None:
    """/unpin - Yanıtlanan veya son sabitlenen mesajı kaldırır."""
    try:
        if message.reply_to_message:
            await message.chat.unpin_message(message_id=message.reply_to_message.message_id)
        else:
            await message.chat.unpin_message()
            
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.CHECKMARK}">☑️</tg-emoji>'
                " <b>SABİTLEME KALDIRILDI.</b>"
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(f"❌ Sabitleme kaldırılamadı: Yetkim yok veya bir hata oluştu. ({str(e)[:50]})")
