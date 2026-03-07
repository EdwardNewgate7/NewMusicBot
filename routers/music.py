"""
╔══════════════════════════════════════════════════════════════╗
║   🎵 Harmony Music - Gelişmiş Müzik Komutları v3.0       ║
║   /oynat, /ara, /indir, /sozler, /loop, /karistir ve daha  ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import logging
import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from config import config
from database.models import add_listen_history, increment_user_plays
from services.music import (
    SongInfo,
    download_song,
    download_video,
    format_duration,
    format_file_size,
    format_views,
    get_video_info,
    is_youtube_url,
    search_youtube,
    search_youtube_detailed,
    validate_cookie_file,
    is_spotify_url,
    get_spotify_metadata,
)
from services.queue import QueueItem, queue_manager
from utils.emoji_ids import emoji
from utils.keyboards import (
    get_music_player_reply_keyboard,
    get_search_results_keyboard,
    get_song_result_keyboard,
    get_loop_keyboard,
    get_quality_select_keyboard,
)

router = Router(name="music")
logger = logging.getLogger("MusicRouter")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                       /oynat KOMUTU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("oynat", "play"))
async def cmd_oynat(message: Message) -> None:
    """
    /oynat [ŞARKI/VİDEO/YANITLA] komutu.
    YouTube'da arar, indirir ve gruba gönderir.
    Cookie.txt ile yaş/bölge kısıtlamalı videolara da erişir.
    """
    args = message.text.split(maxsplit=1)
    
    from services.music import SERVICE_VERSION
    logger.info(f"cmd_oynat triggered. Music Service Version: {SERVICE_VERSION}")

    if len(args) < 2 and not message.reply_to_message:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN BİR ŞARKI ADI YAZIN VEYA BİR "
                "MESAJI YANITLAYIN.</b>\n\n"
                "<b>Kullanım:</b> <code>/oynat şarkı adı</code>\n"
                "<b>URL ile:</b> <code>/oynat youtube_linki</code>"
            ),
            parse_mode="HTML",
        )
        return

    query = args[1] if len(args) > 1 else ""

    # Yanıtlanan mesajdan ses/video çıkar
    if not query and message.reply_to_message:
        if message.reply_to_message.text:
            query = message.reply_to_message.text
        elif message.reply_to_message.caption:
            query = message.reply_to_message.caption
        else:
            query = "Yanıtlanan mesaj"

    # YouTube URL doğrudan mı gönderildi?
    direct_url = is_youtube_url(query)
    
    # Spotify URL mi?
    spotify_url = is_spotify_url(query)

    # Aranıyor mesajı
    cookie_status = config.get_cookie_path()
    cookie_badge = "🍪" if cookie_status else ""

    action_text = 'Spotify linki çözülüyor...' if spotify_url else "YouTube'da aranıyor..."
    status_msg = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.HEADPHONES}">🎶</tg-emoji>'
            f" <b>ARANIYOR:</b> <code>{query[:50]}</code>"
            "\n\n"
            f"<i>{action_text} {cookie_badge}</i>"
        ),
        parse_mode="HTML",
    )

    if spotify_url:
        # Spotify'dan metadata çek
        sp_title, sp_artist, search_query = await get_spotify_metadata(query)
        if search_query:
            query = search_query # YouTube'da bu isimle ara
        else:
            await status_msg.edit_text("❌ Spotify bilgisi alınamadı.")
            return

    if direct_url:
        # Direkt URL verildi, bilgiyi al
        song_info = await get_video_info(query)
        if not song_info:
            await status_msg.edit_text(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    " <b>BU VİDEO BULUNAMADI VEYA ERİŞİLEMİYOR.</b>"
                ),
                parse_mode="HTML",
            )
            return

        # Bilgiyle devam et
        await _download_and_send_song(
            message, status_msg, query, song_info, cookie_badge
        )
    else:
        # YouTube'da ara
        results = await search_youtube(query, max_results=1)

        if not results:
            await status_msg.edit_text(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    f" <b>SONUÇ BULUNAMADI:</b> <code>{query[:50]}</code>"
                ),
                parse_mode="HTML",
            )
            return

        song_result = results[0]

        # Süre kontrolü
        if song_result.duration > config.MAX_SONG_DURATION:
            await status_msg.edit_text(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    f" <b>ŞARKI ÇOK UZUN!</b>\n"
                    f"Süre: {format_duration(song_result.duration)} "
                    f"(Maks: {format_duration(config.MAX_SONG_DURATION)})"
                ),
                parse_mode="HTML",
            )
            return

        await _download_and_send_song(
            message, status_msg,
            song_result.url,
            SongInfo(
                title=song_result.title,
                artist=song_result.artist,
                duration=song_result.duration,
                url=song_result.url,
                thumbnail=song_result.thumbnail,
                video_id=song_result.video_id,
                channel=song_result.channel,
                view_count=song_result.view_count,
            ),
            cookie_badge,
        )


async def _download_and_send_song(
    message: Message,
    status_msg: Message,
    url: str,
    song_info: SongInfo,
    cookie_badge: str,
) -> None:
    """Şarkıyı indirir ve gönderir (ortak mantık)."""
    # İndiriliyor mesajı
    user_link = f"tg://user?id={message.from_user.id}"
    user_name = message.from_user.first_name or "Kullanıcı"
    cmd_text = message.text or f"/oynat {song_info.title}"
    
    # Canlı yayın kontrolü (ön bilgi varsa kullan)
    loading_text = "CANLI YAYIN BAĞLANILIYOR..." if song_info.is_live else "İNDİRİLİYOR..."
    
    await status_msg.edit_text(
        text=(
            f"<blockquote><b><a href=\"{user_link}\">{user_name}</a></b>\n"
            f"{cmd_text}</blockquote>\n"
            f'<tg-emoji emoji-id="{emoji.LOADING}">🌀</tg-emoji> <b>{loading_text}</b>'
        ),
        parse_mode="HTML",
    )

    # İndir
    song = await download_song(url)

    if not song or not song.file_path:
        await status_msg.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>İNDİRME BAŞARISIZ!</b>\n"
                "<i>Tekrar deneyin.</i>"
            ),
            parse_mode="HTML",
        )
        return

    # Kuyruğa ekle
    chat_queue = queue_manager.get(message.chat.id)
    queue_item = QueueItem(
        song=song,
        requested_by=message.from_user.id,
        requested_by_name=message.from_user.first_name or "Kullanıcı",
    )

    if chat_queue.is_playing:
        position = chat_queue.add(queue_item)
        from utils.keyboards import get_queue_added_keyboard
        await status_msg.edit_text(
            text=(
                f"<b>→ Kuyruğa #{position} olarak eklendi</b>\n\n"
                f"▸ <b>Başlık:</b> {song.title}\n"
                f"▸ <b>Süre:</b> {format_duration(song.duration)} dakika\n"
                f"▸ <b>İsteyen:</b> <a href=\"{user_link}\">{user_name}</a> 🎧"
            ),
            parse_mode="HTML",
            reply_markup=get_queue_added_keyboard(url=song.url),
        )
        
    else:
        chat_queue.add(queue_item)
        chat_queue.next()

        # Ses dosyasını Oynat
        try:
            from services.userbot import assistant
            playback_started = await assistant.play_audio(
                message.chat.id, song.file_path
            )
            if not playback_started:
                chat_queue.skip()
                await status_msg.edit_text(
                    text=(
                        f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                        " <b>SES SOHBETİNDE OYNATMA BAŞLATILAMADI.</b>\n"
                        "<i>Asistan hesabını gruba ekleyip tekrar deneyin.</i>"
                    ),
                    parse_mode="HTML",
                )
                return
            
            from utils.keyboards import get_now_playing_keyboard
            
            status_badge = "🔴 Canlı Yayın" if song.is_live else f"⏱ {format_duration(song.duration)} dakika"
            
            await status_msg.edit_text(
                text=(
                    f"<b>→ {'Yayın' if song.is_live else 'Akış'} başlatıldı</b>\n\n"
                    f"▸ <b>Başlık:</b> {song.title}\n"
                    f"▸ <b>Durum:</b> {status_badge}\n"
                    f"▸ <b>İsteyen:</b> <a href=\"{user_link}\">{user_name}</a> 🎧"
                ),
                parse_mode="HTML",
                reply_markup=get_now_playing_keyboard(url=song.url),
            )

            # İstatistik güncelle
            await increment_user_plays(message.from_user.id)
            await add_listen_history(
                user_id=message.from_user.id,
                title=song.title,
                chat_id=message.chat.id,
                artist=song.artist,
                url=song.url,
                duration=song.duration,
            )

        except Exception as e:
            logger.error(f"Oynatma hatası: {e}")
            await status_msg.edit_text(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    f" <b>OYNATMA HATASI:</b> {str(e)[:100]}"
                ),
                parse_mode="HTML",
            )
        finally:
            # Hemen silme! Çünkü arka planda asistan okuyor olabilir.
            # Periyodik temizleyici (periodic_cleanup) zaten eski dosyaları siliyor.
            pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     /ara KOMUTU (YENİ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("ara", "search"))
async def cmd_ara(message: Message) -> None:
    """
    /ara [ŞARKI ADI] komutu.
    YouTube'da arar ve sonuçları inline butonlarla listeler.
    Kullanıcı istediğini seçer.
    """
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.SEARCH}">🔍</tg-emoji>'
                " <b>LÜTFEN BİR ŞARKI ADI YAZIN.</b>\n\n"
                "<b>Kullanım:</b> <code>/ara şarkı adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    query = args[1]

    status_msg = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SEARCH}">🔍</tg-emoji>'
            f" <b>ARANIYOR:</b> <code>{query[:50]}</code>"
            "\n\n"
            "<i>YouTube'da aranıyor...</i>"
        ),
        parse_mode="HTML",
    )

    results = await search_youtube(
        query, max_results=config.DEFAULT_SEARCH_RESULTS,
    )

    if not results:
        await status_msg.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                f" <b>SONUÇ BULUNAMADI:</b> <code>{query[:50]}</code>"
            ),
            parse_mode="HTML",
        )
        return

    # Sonuçları listele
    text_parts = [
        f'<tg-emoji emoji-id="{emoji.SEARCH}">🔍</tg-emoji>'
        f' <b>ARAMA SONUÇLARI:</b> <code>{query[:40]}</code>\n\n'
    ]

    for i, song in enumerate(results, 1):
        dur = format_duration(song.duration)
        artist = song.artist or song.channel or "Bilinmeyen"
        view_text = (
            f" • 👁 {format_views(song.view_count)}"
            if song.view_count else ""
        )
        text_parts.append(
            f"<b>{i}.</b> {song.title}\n"
            f"   👤 {artist} • ⏱ {dur}{view_text}\n\n"
        )

    text_parts.append(
        "<i>İndirmek için numarasına basın:</i>"
    )

    await status_msg.edit_text(
        text="".join(text_parts),
        parse_mode="HTML",
        reply_markup=get_search_results_keyboard(results),
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     /indir KOMUTU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("indir", "download", "dl"))
async def cmd_indir(message: Message) -> None:
    """
    /indir [ŞARKI ADI veya URL] komutu.
    YouTube'dan şarkıyı MP3 olarak indirir ve gönderir.
    """
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN BİR ŞARKI ADI YAZIN.</b>\n\n"
                "<b>Kullanım:</b>\n"
                "  <code>/indir şarkı adı</code>\n"
                "  <code>/indir youtube_linki</code>"
            ),
            parse_mode="HTML",
        )
        return

    query = args[1]
    cookie_badge = "🍪" if config.get_cookie_path() else ""

    status_msg = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.HEART_DOWNLOAD}">💗</tg-emoji>'
            f" <b>ARANIYOR:</b> <code>{query[:50]}</code>"
            "\n\n"
            f"<i>YouTube'da aranıyor... {cookie_badge}</i>"
        ),
        parse_mode="HTML",
    )

    # YouTube URL mi kontrol et
    if is_youtube_url(query):
        download_url = query
        song_info = await get_video_info(query)
        title_display = song_info.title if song_info else query[:50]
    else:
        results = await search_youtube(query, max_results=1)
        if not results:
            await status_msg.edit_text(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    f" <b>SONUÇ BULUNAMADI.</b>"
                ),
                parse_mode="HTML",
            )
            return
        download_url = results[0].url
        title_display = results[0].title

    quality_text = f"{config.AUDIO_QUALITY}kbps {config.AUDIO_FORMAT.upper()}"

    await status_msg.edit_text(
        text=(
            f'<tg-emoji emoji-id="{emoji.HEART_DOWNLOAD}">💗</tg-emoji>'
            f" <b>{title_display}</b>"
            "\n\n"
            f"<i>İndiriliyor... ({quality_text}) {cookie_badge}</i>"
        ),
        parse_mode="HTML",
    )

    song = await download_song(download_url)
    if not song or not song.file_path:
        await status_msg.edit_text(
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

        await message.answer_audio(
            audio=audio_file,
            title=song.title,
            performer=song.artist or None,
            duration=song.duration,
            caption=(
                f'<tg-emoji emoji-id="{emoji.HEART_DOWNLOAD}">💗</tg-emoji>'
                f" <b>İNDİRİLDİ:</b>"
                "\n\n"
                f"🎵 <b>{song.title}</b>\n"
                f"👤 {song.artist or 'Bilinmeyen'}\n"
                f"⏱ {format_duration(song.duration)} • "
                f"📦 {size_text} • 🎚 {song.quality}"
            ),
            parse_mode="HTML",
        )
        await status_msg.delete()
    except Exception as e:
        logger.error(f"Dosya gönderme hatası: {e}")
        await status_msg.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                f" <b>GÖNDERME HATASI.</b>"
            ),
            parse_mode="HTML",
        )
    finally:
        _cleanup(song.file_path)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     /voynat KOMUTU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("voynat", "vplay"))
async def cmd_voynat(message: Message) -> None:
    """
    /voynat [VİDEO/YANITLA] komutu.
    YouTube'dan video indirir ve gönderir.
    """
    args = message.text.split(maxsplit=1)

    if len(args) < 2 and not message.reply_to_message:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN BİR VİDEO ADI YAZIN.</b>\n\n"
                "<b>Kullanım:</b> <code>/voynat video adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    query = args[1] if len(args) > 1 else "yanıtlanan video"
    cookie_badge = "🍪" if config.get_cookie_path() else ""

    status_msg = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.PLAY}">🎵</tg-emoji>'
            f" <b>VİDEO ARANIYOR:</b> <code>{query[:50]}</code> "
            f"{cookie_badge}"
        ),
        parse_mode="HTML",
    )

    # YouTube URL mi kontrol et
    if is_youtube_url(query):
        download_url = query
    else:
        results = await search_youtube(query, max_results=1)
        if not results:
            await status_msg.edit_text(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    " <b>VİDEO BULUNAMADI.</b>"
                ),
                parse_mode="HTML",
            )
            return
        download_url = results[0].url

        msg_stream = "Canlı yayına bağlanılıyor..." if results[0].is_live else f"Video indiriliyor... ({config.VIDEO_QUALITY}p)"
        await status_msg.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.PLAY}">🎵</tg-emoji>'
                f" <b>{results[0].title}</b>\n\n"
                f"<i>{msg_stream} "
                f"{cookie_badge}</i>"
            ),
            parse_mode="HTML",
        )

    video = await download_video(download_url)
    if not video or not video.file_path:
        await status_msg.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>VİDEO İNDİRME BAŞARISIZ!</b>"
            ),
            parse_mode="HTML",
        )
        return

    try:
        from services.userbot import assistant
        playback_started = await assistant.play_audio(
            message.chat.id, video.file_path, is_video=True
        )
        if not playback_started:
            await status_msg.edit_text(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    " <b>VİDEO SES SOHBETİNDE BAŞLATILAMADI.</b>\n"
                    "<i>Asistan hesabını gruba ekleyip tekrar deneyin.</i>"
                ),
                parse_mode="HTML",
            )
            return

        from utils.keyboards import get_now_playing_keyboard
        
        await status_msg.edit_text(
            text=(
                f"<b>→ Video akışı başlatıldı</b>\n\n"
                f"▸ <b>Başlık:</b> {video.title}\n"
                f"▸ <b>Süre:</b> {format_duration(video.duration)} dakika\n"
                f"▸ <b>Kalite:</b> {video.quality}p\n"
                f"▸ <b>İsteyen:</b> {message.from_user.first_name} 🎧"
            ),
            parse_mode="HTML",
            reply_markup=get_now_playing_keyboard(url=video.url),
        )

        # Ayrıca video dosyasını da gönder (opsiyonel ama kullanıcı beğenir)
        video_file = FSInputFile(video.file_path)
        await message.answer_video(
            video=video_file,
            caption=f"🎬 <b>{video.title}</b>",
            parse_mode="HTML",
        )

    except Exception as e:
        logger.error(f"Video oynatma hatası: {e}")
        await status_msg.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>VİDEO OYNATILAMADI.</b>"
            ),
            parse_mode="HTML",
        )
    finally:
        # Temizliği biraz geciktir ki yayın/gönderme bitmiş olsun
        # (Veya temizlemeyip periyodik temizleyicinin silmesini bekle)
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   /sozler KOMUTU (GELİŞMİŞ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("sozler", "lyrics"))
async def cmd_sozler(message: Message) -> None:
    """
    /sozler [ŞARKI ADI] komutu.
    Şarkı sözlerini bulur ve gönderir.
    """
    from services.lyrics import search_lyrics, split_lyrics

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        # Çalan şarkının sözlerini bul
        q = queue_manager.get(message.chat.id)
        if q.current:
            query = f"{q.current.song.artist} - {q.current.song.title}"
        else:
            await message.answer(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    " <b>LÜTFEN BİR ŞARKI ADI YAZIN.</b>\n\n"
                    "<b>Kullanım:</b> <code>/sozler şarkı adı</code>\n"
                    "<i>veya müzik çalarken /sozler yazın.</i>"
                ),
                parse_mode="HTML",
            )
            return
    else:
        query = args[1]

    status_msg = await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.BOOKMARK}">🔖</tg-emoji>'
            f" <b>ŞARKI SÖZLERİ ARANIYOR:</b> "
            f"<code>{query[:50]}</code>\n\n"
            "<i>Lütfen bekleyin...</i>"
        ),
        parse_mode="HTML",
    )

    result = await search_lyrics(query)

    if not result.found:
        await status_msg.edit_text(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                f" <b>ŞARKI SÖZLERİ BULUNAMADI:</b> "
                f"<code>{query[:50]}</code>\n\n"
                "<i>Farklı bir arama terimi deneyin.\n"
                "Örnek: /sozler sanatçı - şarkı adı</i>"
            ),
            parse_mode="HTML",
        )
        return

    # Sözleri böl ve gönder
    parts = split_lyrics(result.lyrics)

    header = (
        f'<tg-emoji emoji-id="{emoji.BOOKMARK}">🔖</tg-emoji>'
        f" <b>ŞARKI SÖZLERİ</b>\n\n"
        f"🎵 <b>{result.title}</b>\n"
        f"👤 {result.artist or 'Bilinmeyen'}\n"
        f"📖 Kaynak: {result.source}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    # İlk parçayı başlıkla gönder
    first_text = header + parts[0]
    await status_msg.edit_text(
        text=first_text,
        parse_mode="HTML",
    )

    # Kalan parçaları ayrı mesaj olarak gönder
    for i, part in enumerate(parts[1:], 2):
        await message.answer(
            text=(
                f"<b>📃 Sayfa {i}/{len(parts)}:</b>\n\n"
                f"{part}"
            ),
            parse_mode="HTML",
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   KONTROL KOMUTLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("poynat", "pplay", "playlistplay"))
async def cmd_poynat(message: Message) -> None:
    """/poynat - Kişisel çalma listesini çalar."""
    from database.models import get_playlist

    playlist = await get_playlist(message.from_user.id)

    if not playlist:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.DISK}">💿</tg-emoji>'
                " <b>ÇALMA LİSTEN BOŞ!</b>\n\n"
                "Şarkı eklemek için: <code>/ekle şarkı adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.DISK}">💿</tg-emoji>'
            f" <b>ÇALMA LİSTEN ({len(playlist)} şarkı):</b>\n\n"
            "Oynatma modu seçin:"
        ),
        parse_mode="HTML",
        reply_markup=get_music_player_reply_keyboard(),
    )


@router.message(Command("dinle", "listen", "player"))
async def cmd_dinle(message: Message) -> None:
    """/dinle - Gelişmiş mini oynatıcıyı açar."""
    cookie_info = "🍪 Cookie.txt: Aktif" if config.get_cookie_path() else "⚪ Cookie.txt: Yok"
    quality_info = f"🎚 Kalite: {config.AUDIO_QUALITY}kbps {config.AUDIO_FORMAT.upper()}"

    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.HEADPHONES}">🎧</tg-emoji>'
            " <b>GELİŞMİŞ MİNİ OYNATICI</b>\n\n"
            "├ KESİNTİSİZ ŞARKI ÇALMA\n"
            "├ ÇALMA LİSTESİNİ KONTROL ET\n"
            "├ ŞARKI DİNLEME ODALARI\n"
            "├ ŞARKI SÖZLERİ BUL\n"
            "├ TEKRAR MODU (TEK/LİSTE)\n"
            "└ VE DAHA FAZLASI!\n\n"
            f"━ {cookie_info}\n"
            f"━ {quality_info}\n\n"
            "Şarkı çalmak için: <code>/oynat şarkı adı</code>\n"
            "Şarkı aramak için: <code>/ara şarkı adı</code>"
        ),
        parse_mode="HTML",
        reply_markup=get_music_player_reply_keyboard(),
    )


@router.message(Command("durdur", "pause"))
async def cmd_durdur(message: Message) -> None:
    """/durdur - Çalanı duraklatır."""
    q = queue_manager.get(message.chat.id)
    if q.is_playing:
        q.pause()
        
        # Sesteki müziği de durdur
        from services.userbot import assistant
        import asyncio
        asyncio.create_task(assistant.pause_stream(message.chat.id))
        
        current = q.current
        title = current.song.title if current else "Bilinmeyen"
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                f" <b>DURAKLATILDI:</b> {title}"
            ),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>ŞU AN ÇALAN BİR ŞEY YOK.</b>"
            ),
            parse_mode="HTML",
        )


@router.message(Command("devam", "resume"))
async def cmd_devam(message: Message) -> None:
    """/devam - Devam ettirir."""
    q = queue_manager.get(message.chat.id)
    if q.is_paused:
        q.resume()
        
        # Sesteki müziği devam ettir
        from services.userbot import assistant
        import asyncio
        asyncio.create_task(assistant.resume_stream(message.chat.id))
        
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.PLAY}">🎵</tg-emoji>'
                " <b>DEVAM ETTİRİLDİ.</b>"
            ),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.PLAY}">🎵</tg-emoji>'
                " <b>DURAKLATILMIŞ MÜZİK YOK.</b>"
            ),
            parse_mode="HTML",
        )


@router.message(Command("atla", "skip", "next"))
async def cmd_atla(message: Message) -> None:
    """/atla - Sıradaki şarkıya geçer."""
    q = queue_manager.get(message.chat.id)
    next_item = q.skip()

    if next_item:
        from services.userbot import assistant
        playback_started = await assistant.play_audio(
            message.chat.id, next_item.song.file_path
        )
        if not playback_started:
            await message.answer(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    " <b>SIRADAKİ ŞARKI BAŞLATILAMADI.</b>"
                ),
                parse_mode="HTML",
            )
            return

        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.PLAY}">🎵</tg-emoji>'
                f" <b>ŞİMDİ ÇALINIYOR:</b> {next_item.song.title}\n"
                f"👤 {next_item.song.artist or 'Bilinmeyen'}"
            ),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>KUYRUKTA ŞARKI KALMADI.</b>"
            ),
            parse_mode="HTML",
        )


@router.message(Command("sira", "queue", "list", "q"))
async def cmd_sira(message: Message) -> None:
    """/sira - Şarkı kuyruğunu görüntüler."""
    q = queue_manager.get(message.chat.id)
    items = q.get_list()

    if not items and not q.current:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.FOLDER}">📁</tg-emoji>'
                " <b>KUYRUK BOŞ.</b>\n\n"
                "Şarkı eklemek için: <code>/oynat şarkı adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    # Loop modu bilgisi
    loop_text = ""
    if q.loop_mode == "one":
        loop_text = "\n🔂 <b>Tekrar Modu:</b> TEK ŞARKI"
    elif q.loop_mode == "all":
        loop_text = "\n🔁 <b>Tekrar Modu:</b> TÜM LİSTE"

    text_parts = [
        f'<tg-emoji emoji-id="{emoji.FOLDER}">📁</tg-emoji>'
        " <b>ŞARKI KUYRUĞU:</b>\n"
    ]

    if q.current:
        import math
        prog_sec = q.get_progress()
        tot_sec = q.current.song.duration
        
        bar_len = 10
        if tot_sec > 0:
            filled = int(math.floor(bar_len * (prog_sec / tot_sec)))
            filled = min(bar_len, max(0, filled))
        else:
            filled = 0
            
        prog_bar = "🟢" * filled + "⚪" * (bar_len - filled)
        prog_str = format_duration(int(prog_sec))
        tot_str = format_duration(tot_sec)

        text_parts.append(
            f"\n▶️ <b>Şimdi çalıyor:</b> {q.current.song.title}\n"
            f"   👤 {q.current.requested_by_name}\n"
            f"   [{prog_bar}] {prog_str} / {tot_str}\n"
        )

    if items:
        text_parts.append("\n<b>Sıradakiler:</b>\n")
        for i, item in enumerate(items[:15], 1):
            dur = format_duration(item.song.duration)
            text_parts.append(
                f"  {i}. {item.song.title} [{dur}]\n"
                f"     📂 {item.requested_by_name}\n"
            )

        if len(items) > 15:
            text_parts.append(
                f"\n<i>...ve {len(items) - 15} şarkı daha</i>"
            )

    text_parts.append(f"\n\n📊 Toplam: {len(items)} şarkı kuyrukta")
    text_parts.append(loop_text)

    await message.answer(
        text="".join(text_parts),
        parse_mode="HTML",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              /loop ve /karistir KOMUTLARI (YENİ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("loop", "tekrar", "repeat", "l"))
async def cmd_loop(message: Message) -> None:
    """
    /loop veya /tekrar - Tekrar modunu değiştirir.
    off → one → all → off
    """
    q = queue_manager.get(message.chat.id)

    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        mode = args[1].lower().strip()
        mode_map = {
            "tek": "one", "one": "one", "1": "one",
            "tum": "all", "all": "all", "liste": "all",
            "kapat": "off", "off": "off", "0": "off",
        }
        new_mode = mode_map.get(mode, None)
        if new_mode:
            q.set_loop(new_mode)
        else:
            await message.answer(
                text=(
                    f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                    " <b>GEÇERSİZ MOD!</b>\n\n"
                    "<b>Kullanım:</b>\n"
                    "  <code>/loop tek</code> - Tek şarkı\n"
                    "  <code>/loop tum</code> - Tüm liste\n"
                    "  <code>/loop kapat</code> - Kapalı"
                ),
                parse_mode="HTML",
            )
            return
    else:
        # Sırayla değiş: off → one → all → off
        cycle = {"off": "one", "one": "all", "all": "off"}
        new_mode = cycle.get(q.loop_mode, "off")
        q.set_loop(new_mode)

    mode_display = {
        "off": "⏹ KAPALI",
        "one": "🔂 TEK ŞARKI TEKRARLA",
        "all": "🔁 TÜM LİSTEYİ TEKRARLA",
    }

    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.PLAY}">🎵</tg-emoji>'
            f" <b>TEKRAR MODU:</b> {mode_display.get(new_mode, 'Bilinmeyen')}"
        ),
        parse_mode="HTML",
        reply_markup=get_loop_keyboard(new_mode),
    )


@router.message(Command("karistir", "shuffle"))
async def cmd_karistir(message: Message) -> None:
    """/karistir veya /shuffle - Kuyruğu karıştırır."""
    q = queue_manager.get(message.chat.id)

    if q.is_empty:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>KUYRUK BOŞ, KARIŞTIRIACAK BİR ŞEY YOK.</b>"
            ),
            parse_mode="HTML",
        )
        return

    q.shuffle()

    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.SPARKLE}">✨</tg-emoji>'
            f" <b>KUYRUK KARIŞTIRILDI!</b> ({q.size} şarkı)"
        ),
        parse_mode="HTML",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              /ses (VOLUME) ve /autodj KOMUTLARI (YENİ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.message(Command("ses", "volume"))
async def cmd_ses(message: Message) -> None:
    """/ses veya /volume [1-200] - Asistanın yayın sesini ayarlar."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].isdigit():
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN BİR SEVİYE GİRİN.</b>\n"
                "<i>Örnek:</i> <code>/ses 50</code> (1-200 arası)"
            ),
            parse_mode="HTML"
        )
        return
        
    volume = int(args[1])
    if volume < 1 or volume > 200:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>SES SEVİYESİ 1 İLE 200 ARASINDA OLMALIDIR.</b>"
            ),
            parse_mode="HTML"
        )
        return

    from services.userbot import assistant
    import asyncio
    success = await assistant.change_volume(message.chat.id, volume)
    
    if success:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.HEADPHONES}">🎧</tg-emoji>'
                f" <b>SES SEVİYESİ AYARLANDI:</b> %{volume}"
            ),
            parse_mode="HTML"
        )
    else:
        await message.answer("⚠️ Ses değiştirilemedi. Asistan aktif olmayabilir.")

@router.message(Command("autodj", "dj", "autoplay"))
async def cmd_autodj(message: Message) -> None:
    """/autodj - Kuyruk bittiğinde otomatik rastgele oynatmayı açar/kapatır."""
    q = queue_manager.get(message.chat.id)
    
    current_state = q.auto_dj
    q.set_auto_dj(not current_state)
    
    new_state = "AÇIK 🟢" if q.auto_dj else "KAPALI 🔴"
    
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.FIRE}">🔥</tg-emoji>'
            f" <b>AUTO-DJ MODU:</b> {new_state}\n\n"
            "<i>(Kuyruğunuz bittiğinde bot aralıksız olarak rastgele hit şarkılar çalmaya devam eder.)</i>"
        ),
        parse_mode="HTML"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                    /cookie KOMUTU (YENİ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("cookie"))
async def cmd_cookie(message: Message) -> None:
    """
    /cookie - Cookie.txt durumunu gösterir (sadece sahipler).
    """
    if message.from_user.id not in config.OWNER_IDS:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>BU KOMUT SADECE BOT SAHİPLERİ İÇİNDİR.</b>"
            ),
            parse_mode="HTML",
        )
        return

    cookie_info = validate_cookie_file()

    status_icon = "✅" if cookie_info["valid"] else "❌"

    text = (
        f'<tg-emoji emoji-id="{emoji.GEAR}">⚙️</tg-emoji>'
        f" <b>COOKIE.TXT DURUMU</b>\n\n"
        f"{status_icon} <b>Durum:</b> "
        f"{'Aktif ve Geçerli' if cookie_info['valid'] else 'Geçersiz veya Yok'}\n"
        f"📂 <b>Yol:</b> <code>{cookie_info['path'] or config.COOKIE_FILE}</code>\n"
        f"📄 <b>Satır Sayısı:</b> {cookie_info['line_count']}\n"
        f"🌐 <b>Domain Sayısı:</b> {cookie_info['domain_count']}\n"
        f"🔄 <b>Etkin:</b> {'Evet' if config.COOKIE_ENABLED else 'Hayır'}\n\n"
        f"💬 {cookie_info['message']}\n\n"
        "<b>━━ SES KALİTESİ ━━</b>\n"
        f"🎚 Kalite: {config.AUDIO_QUALITY}kbps\n"
        f"📀 Format: {config.AUDIO_FORMAT.upper()}\n"
        f"🎬 Video: {config.VIDEO_QUALITY}p"
    )

    await message.answer(text=text, parse_mode="HTML")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                      DİĞER KOMUTLAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.message(Command("ileri", "forward", "ff"))
async def cmd_ileri(message: Message) -> None:
    """/ileri [SN] - Şarkıyı ileri sarar."""
    args = message.text.split(maxsplit=1)
    seconds = args[1] if len(args) > 1 else "10"
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.PLAY}">🎵</tg-emoji>'
            f" <b>ŞARKI {seconds} SANİYE İLERİ SARILDI.</b>"
        ),
        parse_mode="HTML",
    )


@router.message(Command("geri", "rewind", "rw"))
async def cmd_geri(message: Message) -> None:
    """/geri [SN] - Şarkıyı geri sarar."""
    args = message.text.split(maxsplit=1)
    seconds = args[1] if len(args) > 1 else "10"
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.REWIND}">⏪</tg-emoji>'
            f" <b>ŞARKI {seconds} SANİYE GERİ SARILDI.</b>"
        ),
        parse_mode="HTML",
    )


@router.message(Command("son", "bitir", "stop", "end", "terminate"))
async def cmd_son(message: Message) -> None:
    """/son veya /bitir - Aktif müziği anında sonlandırır."""
    q = queue_manager.get(message.chat.id)
    q.stop()
    
    # Asistan sesi de kapatsın
    from services.userbot import assistant
    import asyncio
    asyncio.create_task(assistant.stop_stream(message.chat.id))
    
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
            " <b>AKTİF MÜZİK SONLANDIRILDI.</b> "
            "Kuyruk temizlendi."
        ),
        parse_mode="HTML",
    )


@router.message(Command("vindir", "vdownload", "vdl"))
async def cmd_vindir(message: Message) -> None:
    """/vindir [VİDEO ADI] - Videoyu indirir."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN VİDEO ADI YAZIN.</b>\n\n"
                "<b>Kullanım:</b> <code>/vindir video adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    # /voynat ile aynı mantık
    message.text = f"/voynat {args[1]}"
    await cmd_voynat(message)


@router.message(Command("kalite", "quality"))
async def cmd_kalite(message: Message) -> None:
    """
    /kalite - Mevcut ses kalitesi bilgisini gösterir.
    """
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.HEADPHONES}">🎧</tg-emoji>'
            " <b>SES KALİTESİ AYARLARI</b>\n\n"
            f"🎚 <b>Ses Kalitesi:</b> {config.AUDIO_QUALITY}kbps\n"
            f"📀 <b>Ses Formatı:</b> {config.AUDIO_FORMAT.upper()}\n"
            f"🎬 <b>Video Kalitesi:</b> {config.VIDEO_QUALITY}p\n\n"
            f"🍪 <b>Cookie:</b> "
            f"{'Aktif' if config.get_cookie_path() else 'Pasif'}\n"
            f"📦 <b>Maks. Dosya:</b> "
            f"{format_file_size(config.MAX_AUDIO_FILE_SIZE)}\n"
            f"⏱ <b>Maks. Süre:</b> "
            f"{format_duration(config.MAX_SONG_DURATION)}"
        ),
        parse_mode="HTML",
        reply_markup=get_quality_select_keyboard(),
    )


@router.message(Command("ses", "volume", "vol"))
async def cmd_ses(message: Message) -> None:
    """/ses [1-200] komutu. Botun ses düzeyini ayarlar."""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.AUDIO_BARS}">📶</tg-emoji>'
                " <b>MEVCUT SES AYARI:</b>\n\n"
                "Sesi değiştirmek için:\n"
                "<b>Kullanım:</b> <code>/ses 50</code> (1-200 arası)"
            ),
            parse_mode="HTML"
        )
        return

    try:
        vol = int(args[1].strip())
        if vol < 1 or vol > 200:
            raise ValueError
    except ValueError:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>LÜTFEN 1 İLE 200 ARASINDA BİR DEĞER GİRİN!</b>"
            ),
            parse_mode="HTML"
        )
        return

    from services.userbot import assistant
    if not assistant.is_started:
        await message.answer("⚠️ Asistan aktif değil.")
        return

    chat_id = message.chat.id
    success = await assistant.change_volume(chat_id, vol)
    
    if success:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.AUDIO_BARS}">📶</tg-emoji>'
                f" <b>SES SEVİYESİ %{vol} OLARAK AYARLANDI!</b>"
            ),
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Ses seviyesi değiştirilemedi. Sesli sohbette bir şarkı çalmıyor olabilir.")


@router.message(Command("calan", "np", "nowplaying", "playing"))
async def cmd_calan(message: Message) -> None:
    """
    /calan veya /np - Şu an çalan şarkıyı gösterir.
    """
    q = queue_manager.get(message.chat.id)

    if not q.current:
        await message.answer(
            text=(
                f'<tg-emoji emoji-id="{emoji.STOP}">⛔</tg-emoji>'
                " <b>ŞU AN ÇALAN BİR ŞARKI YOK.</b>\n\n"
                "Şarkı çalmak için: <code>/oynat şarkı adı</code>"
            ),
            parse_mode="HTML",
        )
        return

    current = q.current
    song = current.song

    # Durum bilgisi
    status = "⏸ DURAKLATILDI" if q.is_paused else "▶️ ÇALINIYOR"

    # Loop bilgisi
    loop_text = ""
    if q.loop_mode == "one":
        loop_text = "\n🔂 Tekrar: TEK ŞARKI"
    elif q.loop_mode == "all":
        loop_text = "\n🔁 Tekrar: TÜM LİSTE"

    # İlerleme Çubuğu (Progress Bar)
    import math
    prog_sec = q.get_progress()
    tot_sec = song.duration
    
    bar_len = 15
    if tot_sec > 0:
        filled = int(math.floor(bar_len * (prog_sec / tot_sec)))
        filled = min(bar_len, max(0, filled))
    else:
        filled = 0
        
    prog_bar = "🟢" * filled + "⚪" * (bar_len - filled)
    prog_str = format_duration(int(prog_sec))
    tot_str = format_duration(tot_sec)

    quality_text = f" • 🎚 {song.quality}" if song.quality else ""
    await message.answer(
        text=(
            f'<tg-emoji emoji-id="{emoji.HEADPHONES}">🎧</tg-emoji>'
            f" <b>{status}</b>\n\n"
            f"🎵 <b>{song.title}</b>\n"
            f"👤 {song.artist or 'Bilinmeyen'}\n"
            f"┣ <code>[{prog_bar}]</code>\n"
            f"┗ ⏱ {prog_str} / {tot_str}{quality_text}\n\n"
            f"📂 Talep eden: {current.requested_by_name}\n"
            f"📋 Kuyrukta: {q.size} şarkı"
            f"{loop_text}"
        ),
        parse_mode="HTML",
    )


def _cleanup(path: str) -> None:
    """Geçici dosyayı temizler."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
