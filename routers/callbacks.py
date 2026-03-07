"""
╔══════════════════════════════════════════════════════════════╗
║    🎵 Harmony Music - Callback Query Handler'ları v3.0    ║
║    Arama sonucu, loop, kalite ve menü callback'leri         ║
╚══════════════════════════════════════════════════════════════╝
"""

import logging
import os

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile

from config import config
from database.models import add_listen_history, increment_user_plays
from services.music import (
    download_song,
    format_duration,
    format_file_size,
    validate_cookie_file,
)
from services.queue import QueueItem, queue_manager
from utils.emoji_ids import emoji
from utils.keyboards import (
    get_back_to_commands_keyboard,
    get_commands_categories_keyboard,
    get_loop_keyboard,
    get_start_inline_keyboard,
)
from utils.texts import (
    commands_main_text,
    control_commands_text,
    developer_text,
    download_commands_text,
    music_play_commands_text,
    other_commands_text,
    playlist_commands_text,
    start_text,
    tagging_commands_text,
)

router = Router(name="callbacks")
logger = logging.getLogger("CallbackRouter")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   KOMUTLAR ANA MENÜ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data == "cmd_main")
async def cb_commands_main(callback: CallbackQuery) -> None:
    """KOMUTLAR butonuna basıldığında komut kategorilerini gösterir."""
    await callback.message.edit_text(
        text=commands_main_text(),
        parse_mode="HTML",
        reply_markup=get_commands_categories_keyboard(),
    )
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                ANA MENÜYE GERİ DÖN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data == "back_to_start")
async def cb_back_to_start(callback: CallbackQuery) -> None:
    """Ana menüye (/start mesajına) geri döner."""
    user_first_name = callback.from_user.first_name or "Kullanıcı"

    keyboard = get_start_inline_keyboard(
        bot_username=config.BOT_USERNAME,
        assistant_username=config.ASSISTANT_BOT_USERNAME.lstrip("@"),
        dev1_username=config.DEV_USERNAME,
        dev2_username=config.DEV2_USERNAME,
    )

    await callback.message.edit_text(
        text=start_text(user_first_name),
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                OYNATMA KOMUTLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data == "cmd_play")
async def cb_play_commands(callback: CallbackQuery) -> None:
    """Müzik oynatma komutları kategorisini gösterir."""
    await callback.message.edit_text(
        text=music_play_commands_text(),
        parse_mode="HTML",
        reply_markup=get_back_to_commands_keyboard(),
    )
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                KONTROL KOMUTLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data == "cmd_control")
async def cb_control_commands(callback: CallbackQuery) -> None:
    """Kontrol komutları kategorisini gösterir."""
    await callback.message.edit_text(
        text=control_commands_text(),
        parse_mode="HTML",
        reply_markup=get_back_to_commands_keyboard(),
    )
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                ÇALMA LİSTESİ KOMUTLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data == "cmd_playlist")
async def cb_playlist_commands(callback: CallbackQuery) -> None:
    """Çalma listesi komutları kategorisini gösterir."""
    await callback.message.edit_text(
        text=playlist_commands_text(),
        parse_mode="HTML",
        reply_markup=get_back_to_commands_keyboard(),
    )
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                DİĞER KOMUTLAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data == "cmd_other")
async def cb_other_commands(callback: CallbackQuery) -> None:
    """Diğer komutlar kategorisini gösterir."""
    await callback.message.edit_text(
        text=other_commands_text(),
        parse_mode="HTML",
        reply_markup=get_back_to_commands_keyboard(),
    )
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                ETİKETLEME KOMUTLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data == "cmd_tagging")
async def cb_tagging_commands(callback: CallbackQuery) -> None:
    """Etiketleme komutları kategorisini gösterir."""
    await callback.message.edit_text(
        text=tagging_commands_text(),
        parse_mode="HTML",
        reply_markup=get_back_to_commands_keyboard(),
    )
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                İNDİRME KOMUTLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data == "cmd_download")
async def cb_download_commands(callback: CallbackQuery) -> None:
    """İndirme komutları kategorisini gösterir."""
    await callback.message.edit_text(
        text=download_commands_text(),
        parse_mode="HTML",
        reply_markup=get_back_to_commands_keyboard(),
    )
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                GELİŞTİRİCİ BİLGİLERİ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data == "cmd_developer")
async def cb_developer_info(callback: CallbackQuery) -> None:
    """Geliştirici bilgilerini gösterir."""
    await callback.message.edit_text(
        text=developer_text(),
        parse_mode="HTML",
        reply_markup=get_back_to_commands_keyboard(),
    )
    await callback.answer()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ARAMA SONUCU OYNATMA CALLBACK'LERİ (YENİ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data.startswith("splay_"))
async def cb_search_play(callback: CallbackQuery) -> None:
    """Arama sonucundan şarkıyı oynatır."""
    video_id = callback.data.replace("splay_", "")

    if not video_id:
        await callback.answer("❌ Geçersiz video!", show_alert=True)
        return

    url = f"https://youtube.com/watch?v={video_id}"
    cookie_badge = "🍪" if config.get_cookie_path() else ""
    quality_text = f"{config.AUDIO_QUALITY}kbps {config.AUDIO_FORMAT.upper()}"

    await callback.message.edit_text(
        text=(
            f'<tg-emoji emoji-id="{emoji.HEART_DOWNLOAD}">💗</tg-emoji>'
            f" <b>İNDİRİLİYOR...</b> ({quality_text}) {cookie_badge}\n\n"
            "<i>Lütfen bekleyin...</i>"
        ),
        parse_mode="HTML",
    )

    song = await download_song(url)

    if not song or not song.file_path:
        await callback.message.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>İNDİRME BAŞARISIZ!</b>"
            ),
            parse_mode="HTML",
        )
        return

    # Kuyruğa ekle
    chat_queue = queue_manager.get(callback.message.chat.id)
    queue_item = QueueItem(
        song=song,
        requested_by=callback.from_user.id,
        requested_by_name=callback.from_user.first_name or "Kullanıcı",
    )

    if chat_queue.is_playing:
        position = chat_queue.add(queue_item)
        await callback.message.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.PLAY}">🎵</tg-emoji>'
                f" <b>KUYRUĞA EKLENDİ (#{position}):</b>\n\n"
                f"🎵 <b>{song.title}</b>\n"
                f"👤 {song.artist or 'Bilinmeyen'} • "
                f"⏱ {format_duration(song.duration)}"
            ),
            parse_mode="HTML",
        )
    else:
        chat_queue.add(queue_item)
        chat_queue.next()

        try:
            from services.userbot import assistant
            
            playback_started = await assistant.play_audio(
                callback.message.chat.id, song.file_path
            )
            if playback_started:
                from utils.keyboards import get_now_playing_keyboard
                status_badge = "🔴 Canlı Yayın" if song.is_live else f"⏱ {format_duration(song.duration)} dakika"
                await callback.message.edit_text(
                    text=(
                        f"<b>→ {'Yayın' if song.is_live else 'Akış'} başlatıldı</b>\n\n"
                        f"▸ <b>Başlık:</b> {song.title}\n"
                        f"▸ <b>Durum:</b> {status_badge}\n"
                        f"▸ <b>İsteyen:</b> {callback.from_user.first_name} 🎧"
                    ),
                    parse_mode="HTML",
                    reply_markup=get_now_playing_keyboard(url=song.url),
                )
            else:
                chat_queue.skip()
                # Private chat veya asistan kapalıysa dosyayı gönder
                audio_file = FSInputFile(
                    song.file_path,
                    filename=f"{song.title}.{config.AUDIO_FORMAT}",
                )
                size_text = format_file_size(song.file_size)

                await callback.message.answer_audio(
                    audio=audio_file,
                    title=song.title,
                    performer=song.artist or None,
                    duration=song.duration,
                    caption=(
                        f'<tg-emoji emoji-id="{emoji.PLAY}">🎵</tg-emoji>'
                        f" <b>ÇALINIYOR:</b>\n\n"
                        f"🎵 <b>{song.title}</b>\n"
                        f"👤 {song.artist or 'Bilinmeyen'}\n"
                        f"⏱ {format_duration(song.duration)} • "
                        f"📦 {size_text}\n"
                        f"📂 {queue_item.requested_by_name}"
                    ),
                    parse_mode="HTML",
                )
                await callback.message.delete()

            await increment_user_plays(callback.from_user.id)
            await add_listen_history(
                user_id=callback.from_user.id,
                title=song.title,
                chat_id=callback.message.chat.id,
                artist=song.artist,
                url=song.url,
                duration=song.duration,
            )

        except Exception as e:
            logger.error(f"Oynatma hatası (callback): {e}")
            await callback.message.edit_text(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    f" <b>OYNATMA HATASI:</b> {str(e)[:100]}"
                ),
                parse_mode="HTML",
            )

        finally:
            pass


@router.callback_query(F.data.startswith("sdl_"))
async def cb_search_download(callback: CallbackQuery) -> None:
    """Arama sonucundan şarkıyı indirir."""
    video_id = callback.data.replace("sdl_", "")

    if not video_id:
        await callback.answer("❌ Geçersiz video!", show_alert=True)
        return

    url = f"https://youtube.com/watch?v={video_id}"
    cookie_badge = "🍪" if config.get_cookie_path() else ""
    quality_text = f"{config.AUDIO_QUALITY}kbps {config.AUDIO_FORMAT.upper()}"

    await callback.message.edit_text(
        text=(
            f'<tg-emoji emoji-id="{emoji.HEART_DOWNLOAD}">💗</tg-emoji>'
            f" <b>İNDİRİLİYOR...</b> ({quality_text}) {cookie_badge}"
        ),
        parse_mode="HTML",
    )

    song = await download_song(url)

    if not song or not song.file_path:
        await callback.message.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>İNDİRME BAŞARISIZ!</b>"
            ),
            parse_mode="HTML",
        )
        return

    try:
        audio_file = FSInputFile(
            song.file_path,
            filename=f"{song.title}.{config.AUDIO_FORMAT}",
        )
        size_text = format_file_size(song.file_size)

        await callback.message.answer_audio(
            audio=audio_file,
            title=song.title,
            performer=song.artist or None,
            duration=song.duration,
            caption=(
                f'<tg-emoji emoji-id="{emoji.HEART_DOWNLOAD}">💗</tg-emoji>'
                f" <b>İNDİRİLDİ:</b>\n\n"
                f"🎵 <b>{song.title}</b>\n"
                f"👤 {song.artist or 'Bilinmeyen'}\n"
                f"⏱ {format_duration(song.duration)} • "
                f"📦 {size_text} • 🎚 {song.quality}"
            ),
            parse_mode="HTML",
        )
        await callback.message.delete()
    except Exception as e:
        logger.error(f"Dosya gönderme hatası: {e}")
        await callback.message.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>GÖNDERME HATASI.</b>"
            ),
            parse_mode="HTML",
        )
    finally:
        _cleanup(song.file_path)


@router.callback_query(F.data == "search_cancel")
async def cb_search_cancel(callback: CallbackQuery) -> None:
    """Arama sonuçlarını iptal eder."""
    await callback.message.delete()
    await callback.answer("✅ Arama iptal edildi.")


@router.callback_query(F.data == "skip_now")
async def cb_skip_now(callback: CallbackQuery) -> None:
    """Mevcut şarkıyı atlar ve sıradakine geçer."""
    q = queue_manager.get(callback.message.chat.id)
    if not q.is_playing:
        await callback.answer("❌ Şu an çalan bir şarkı yok!", show_alert=True)
        return

    # Atla (Sıradakini al)
    next_item = q.skip()

    if next_item:
        from services.userbot import assistant
        playback_started = await assistant.play_audio(
            callback.message.chat.id, next_item.song.file_path
        )
        if not playback_started:
            await callback.answer(
                "❌ Sıradaki şarkı sesli sohbette başlatılamadı.",
                show_alert=True,
            )
            return

        from utils.keyboards import get_now_playing_keyboard
        status_badge = "🔴 Canlı Yayın" if next_item.song.is_live else f"⏱ {format_duration(next_item.song.duration)} dakika"
        
        await callback.message.edit_text(
            text=(
                f"<b>→ {'Yayın' if next_item.song.is_live else 'Akış'} başlatıldı</b>\n\n"
                f"▸ <b>Başlık:</b> {next_item.song.title}\n"
                f"▸ <b>Durum:</b> {status_badge}\n"
                f"▸ <b>İsteyen:</b> {next_item.requested_by_name} 🎧"
            ),
            parse_mode="HTML",
            reply_markup=get_now_playing_keyboard(url=next_item.song.url),
        )
        await callback.answer("⏭ Sıradaki şarkıya geçildi!")
    else:
        # Kuyruk bitti
        await callback.answer("✅ Kuyruk bitti, yayın durduruluyor...", show_alert=True)
        from services.userbot import assistant
        if assistant.is_started:
            await assistant.stop_stream(callback.message.chat.id)
        
        await callback.message.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>HIZLI GEÇİŞ YAPILDI. KUYRUK TAMAMLANDI.</b>"
            ),
            parse_mode="HTML",
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              LOOP MODU CALLBACK'LERİ (YENİ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data.startswith("loop_"))
async def cb_loop_mode(callback: CallbackQuery) -> None:
    """Loop modunu değiştirir."""
    mode = callback.data.replace("loop_", "")

    if mode not in ("off", "one", "all"):
        await callback.answer("❌ Geçersiz mod!", show_alert=True)
        return

    q = queue_manager.get(callback.message.chat.id)
    q.set_loop(mode)

    mode_display = {
        "off": "⏹ KAPALI",
        "one": "🔂 TEK ŞARKI TEKRARLA",
        "all": "🔁 TÜM LİSTEYİ TEKRARLA",
    }

    await callback.message.edit_text(
        text=(
            f'<tg-emoji emoji-id="{emoji.PLAY}">🎵</tg-emoji>'
            f" <b>TEKRAR MODU:</b> {mode_display.get(mode, 'Bilinmeyen')}"
        ),
        parse_mode="HTML",
        reply_markup=get_loop_keyboard(mode),
    )
    await callback.answer(f"✅ {mode_display.get(mode, '')}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          COOKİE DURUMU CALLBACK (YENİ - Panel)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.callback_query(F.data == "panel_cookie")
async def cb_panel_cookie(callback: CallbackQuery) -> None:
    """Panel'den cookie durumunu gösterir."""
    if callback.from_user.id not in config.OWNER_IDS:
        await callback.answer(
            "❌ Bu işlem sadece bot sahipleri içindir!",
            show_alert=True,
        )
        return

    cookie_info = validate_cookie_file()
    status_icon = "✅" if cookie_info["valid"] else "❌"

    text = (
        f'<tg-emoji emoji-id="{emoji.GEAR}">⚙️</tg-emoji>'
        f" <b>COOKIE.TXT DURUMU</b>\n\n"
        f"{status_icon} <b>Durum:</b> "
        f"{'Aktif ve Geçerli' if cookie_info['valid'] else 'Geçersiz/Yok'}\n"
        f"📂 <b>Yol:</b> <code>{cookie_info['path'] or config.COOKIE_FILE}</code>\n"
        f"📄 <b>Satır:</b> {cookie_info['line_count']}\n"
        f"🌐 <b>Domain:</b> {cookie_info['domain_count']}\n\n"
        f"💬 {cookie_info['message']}\n\n"
        "<b>━━ SES KALİTESİ ━━</b>\n"
        f"🎚 Kalite: {config.AUDIO_QUALITY}kbps\n"
        f"📀 Format: {config.AUDIO_FORMAT.upper()}\n"
        f"🎬 Video: {config.VIDEO_QUALITY}p"
    )

    from utils.keyboards import get_back_to_commands_keyboard
    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_back_to_commands_keyboard(),
    )
    await callback.answer()


def _cleanup(path: str) -> None:
    """Geçici dosyayı temizler."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
