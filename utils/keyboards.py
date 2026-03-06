"""
╔══════════════════════════════════════════════════════════════╗
║       🎵 Harmony Music - Klavye Tanımlamaları v3.0        ║
║       Gelişmiş arama, loop, kalite ve oynatıcı klavyeleri   ║
╚══════════════════════════════════════════════════════════════╝

Butonlarda kullanılan özel parametreler:
  • style='primary'   → Mavi renk
  • style='success'   → Yeşil renk
  • style='danger'    → Kırmızı renk
  • icon_custom_emoji_id → Buton metninin soluna özel emoji ikonu
"""

from __future__ import annotations

from typing import Any

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from utils.emoji_ids import emoji


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   /START  INLINE KLAVYE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_start_inline_keyboard(
    bot_username: str,
    assistant_username: str,
    dev1_username: str,
    dev2_username: str,
) -> InlineKeyboardMarkup:
    """
    /start komutu sonrası gösterilen ana Inline klavye.
      [👥 BENİ EKLE]  [🐴 ASİSTANI EKLE]
      [👑 GELİŞTİRİCİ]  [🌸 GELİŞTİRİCİ]
      [☑️ KOMUTLAR]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="BENİ EKLE",
                    url=f"tg://resolve?domain={bot_username.lstrip('@')}&startgroup=true",
                    icon_custom_emoji_id=emoji.GROUP_ADD,
                    style="success",
                ),
                InlineKeyboardButton(
                    text="ASİSTANI EKLE",
                    url=f"tg://resolve?domain={assistant_username.lstrip('@')}",
                    icon_custom_emoji_id=emoji.MEGAPHONE_PLUS,
                    style="success",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="GELİŞTİRİCİ",
                    url=f"tg://resolve?domain={dev1_username.lstrip('@')}",
                    icon_custom_emoji_id=emoji.CROWN,
                    style="danger",
                ),
                InlineKeyboardButton(
                    text="GELİŞTİRİCİ",
                    url=f"tg://resolve?domain={dev2_username.lstrip('@')}",
                    icon_custom_emoji_id=emoji.LION,
                    style="danger",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="KOMUTLAR",
                    callback_data="cmd_main",
                    icon_custom_emoji_id=emoji.COMMANDS,
                    style="primary",
                ),
            ],
        ]
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              KOMUT KATEGORİLERİ INLINE KLAVYE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_commands_categories_keyboard() -> InlineKeyboardMarkup:
    """
    Komut kategorileri menüsü.
      [🎵 OYNATMA]  [⚙️ KONTROL]
      [📁 ÇALMA LİSTESİ]  [📊 DİĞER]
      [🔖 ETİKETLEME]  [💗 İNDİRME]
      [👑 GELİŞTİRİCİ]
      [⏪ ANA MENÜYE DÖN]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="OYNATMA",
                    callback_data="cmd_play",
                    icon_custom_emoji_id=emoji.CMD_PLAY,
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="KONTROL",
                    callback_data="cmd_control",
                    icon_custom_emoji_id=emoji.CMD_CONTROL,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="ÇALMA LİSTESİ",
                    callback_data="cmd_playlist",
                    icon_custom_emoji_id=emoji.CMD_PLAYLIST,
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="DİĞER",
                    callback_data="cmd_other",
                    icon_custom_emoji_id=emoji.CMD_OTHER,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="ETİKETLEME",
                    callback_data="cmd_tagging",
                    icon_custom_emoji_id=emoji.CMD_TAGGING,
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="İNDİRME",
                    callback_data="cmd_download",
                    icon_custom_emoji_id=emoji.CMD_DOWNLOAD,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="GELİŞTİRİCİ",
                    callback_data="cmd_developer",
                    icon_custom_emoji_id=emoji.CROWN,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="ANA MENÜYE DÖN",
                    callback_data="back_to_start",
                    icon_custom_emoji_id=emoji.REWIND,
                    style="danger",
                ),
            ],
        ]
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                    GERİ DÖN BUTONLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_back_to_commands_keyboard() -> InlineKeyboardMarkup:
    """Komut detay sayfalarındaki 'GERİ DÖN' butonu."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="GERİ DÖN",
                    callback_data="cmd_main",
                    icon_custom_emoji_id=emoji.REWIND,
                    style="danger",
                ),
            ],
        ]
    )


def get_back_to_start_keyboard() -> InlineKeyboardMarkup:
    """Ana menüye dönüş butonu."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="ANA MENÜYE DÖN",
                    callback_data="back_to_start",
                    icon_custom_emoji_id=emoji.REWIND,
                    style="danger",
                ),
            ],
        ]
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#               MÜZIK OYNATICI REPLY KLAVYE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_music_player_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Müzik çalarken gösterilen Reply klavye.
    Kontrol butonları renklendirilmiş olarak sunulur.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⏮ Önceki", style="primary"),
                KeyboardButton(text="⏸ Duraklat", style="danger"),
                KeyboardButton(text="⏭ Sonraki", style="primary"),
            ],
            [
                KeyboardButton(text="🔀 Karışık", style="success"),
                KeyboardButton(text="🔁 Tekrarla", style="success"),
                KeyboardButton(text="📋 Sıra", style="primary"),
            ],
            [
                KeyboardButton(text="🔍 Ara", style="primary"),
                KeyboardButton(text="📝 Sözler", style="success"),
                KeyboardButton(text="🎧 Çalan", style="primary"),
            ],
            [
                KeyboardButton(text="⏹ Durdur", style="danger"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="🎵 Şarkı adı yazın veya komut girin...",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#             ARAMA SONUÇLARI INLINE KLAVYE (YENİ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_search_results_keyboard(
    results: list[Any],
) -> InlineKeyboardMarkup:
    """
    /ara komutu ile bulunan sonuçlar için inline butonlar.
    Her sonuç için [OYNAT] ve [İNDİR] butonları.
    """
    keyboard = []

    for i, song in enumerate(results):
        video_id = song.video_id or ""
        row = [
            InlineKeyboardButton(
                text=f"{i+1}. OYNAT",
                callback_data=f"splay_{video_id}",
                icon_custom_emoji_id=emoji.PLAY,
                style="success",
            ),
            InlineKeyboardButton(
                text=f"{i+1}. İNDİR",
                callback_data=f"sdl_{video_id}",
                icon_custom_emoji_id=emoji.HEART_DOWNLOAD,
                style="primary",
            ),
        ]
        keyboard.append(row)

    # İptal butonu
    keyboard.append([
        InlineKeyboardButton(
            text="İPTAL",
            callback_data="search_cancel",
            icon_custom_emoji_id=emoji.STOP,
            style="danger",
        ),
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              LOOP MODU INLINE KLAVYE (YENİ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_loop_keyboard(current_mode: str = "off") -> InlineKeyboardMarkup:
    """
    Tekrar modu seçim klavyesi.
    Aktif modun yanına ✓ eklenir.
    """
    off_text = "⏹ KAPALI" + (" ✓" if current_mode == "off" else "")
    one_text = "🔂 TEK ŞARKI" + (" ✓" if current_mode == "one" else "")
    all_text = "🔁 TÜM LİSTE" + (" ✓" if current_mode == "all" else "")

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=off_text,
                    callback_data="loop_off",
                    style="danger" if current_mode == "off" else "primary",
                ),
                InlineKeyboardButton(
                    text=one_text,
                    callback_data="loop_one",
                    style="success" if current_mode == "one" else "primary",
                ),
                InlineKeyboardButton(
                    text=all_text,
                    callback_data="loop_all",
                    style="success" if current_mode == "all" else "primary",
                ),
            ],
        ]
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#            KALİTE SEÇİM INLINE KLAVYE (YENİ)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_quality_select_keyboard() -> InlineKeyboardMarkup:
    """Ses kalitesi bilgi klavyesi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="128kbps",
                    callback_data="quality_128",
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="192kbps",
                    callback_data="quality_192",
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="256kbps",
                    callback_data="quality_256",
                    style="success",
                ),
                InlineKeyboardButton(
                    text="320kbps",
                    callback_data="quality_320",
                    style="success",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="GERİ DÖN",
                    callback_data="back_to_start",
                    icon_custom_emoji_id=emoji.REWIND,
                    style="danger",
                ),
            ],
        ]
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                  AYARLAR INLINE KLAVYE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Bot ayarları inline klavyesi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="SESLİ KORUMA",
                    callback_data="setting_voice_protection",
                    icon_custom_emoji_id=emoji.KEY,
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="HOŞGELDİN MESAJI",
                    callback_data="setting_welcome",
                    icon_custom_emoji_id=emoji.SPARKLE,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="SIRA BİLDİRİM",
                    callback_data="setting_queue_notify",
                    icon_custom_emoji_id=emoji.CHART,
                    style="success",
                ),
                InlineKeyboardButton(
                    text="KAPAK FOTOĞRAFI",
                    callback_data="setting_cover_photo",
                    icon_custom_emoji_id=emoji.FOLDER,
                    style="success",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="TEMİZLİK MODU",
                    callback_data="setting_cleanup",
                    icon_custom_emoji_id=emoji.STOP,
                    style="danger",
                ),
                InlineKeyboardButton(
                    text="OYNATMA YETKİSİ",
                    callback_data="setting_play_permission",
                    icon_custom_emoji_id=emoji.CHECKMARK,
                    style="danger",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="GERİ DÖN",
                    callback_data="back_to_start",
                    icon_custom_emoji_id=emoji.REWIND,
                    style="danger",
                ),
            ],
        ]
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                ŞARKI ARAMA SONUÇLARI INLINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_song_result_keyboard(song_id: str) -> InlineKeyboardMarkup:
    """Şarkı arama sonucu için inline butonlar."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="OYNAT",
                    callback_data=f"play_{song_id}",
                    icon_custom_emoji_id=emoji.PLAY,
                    style="success",
                ),
                InlineKeyboardButton(
                    text="SIRA EKLE",
                    callback_data=f"queue_{song_id}",
                    icon_custom_emoji_id=emoji.FOLDER,
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="İNDİR",
                    callback_data=f"download_{song_id}",
                    icon_custom_emoji_id=emoji.HEART_DOWNLOAD,
                    style="danger",
                ),
            ],
        ]
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              ÇALMA LİSTESİ YÖNETİMİ INLINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_playlist_manage_keyboard() -> InlineKeyboardMarkup:
    """Çalma listesi yönetim klavyesi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="SIRAYLA ÇAL",
                    callback_data="pl_play_ordered",
                    icon_custom_emoji_id=emoji.PLAY,
                    style="success",
                ),
                InlineKeyboardButton(
                    text="KARIŞIK ÇAL",
                    callback_data="pl_play_shuffle",
                    icon_custom_emoji_id=emoji.PLAY,
                    style="success",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="LİSTEYİ GÖRÜNTÜLE",
                    callback_data="pl_view",
                    icon_custom_emoji_id=emoji.FOLDER,
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="LİSTEYİ SİL",
                    callback_data="pl_clear",
                    icon_custom_emoji_id=emoji.STOP,
                    style="danger",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="GERİ DÖN",
                    callback_data="back_to_start",
                    icon_custom_emoji_id=emoji.REWIND,
                    style="danger",
                ),
            ],
        ]
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#               YÖNETİCİ PANELİ INLINE KLAVYE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Yönetici paneli inline klavyesi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="HIZ TESTİ",
                    callback_data="panel_speed_test",
                    icon_custom_emoji_id=emoji.ROCKET,
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="SES/VİDEO KALİTESİ",
                    callback_data="panel_quality",
                    icon_custom_emoji_id=emoji.VIDEO_QUALITY,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="İSTATİSTİKLER",
                    callback_data="panel_stats",
                    icon_custom_emoji_id=emoji.STATS,
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="GELİŞMİŞ REKLAM",
                    callback_data="panel_broadcast",
                    icon_custom_emoji_id=emoji.BROADCAST,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="ÖNBELLEK TEMİZLE",
                    callback_data="panel_cache_clear",
                    icon_custom_emoji_id=emoji.BROOM,
                    style="success",
                ),
                InlineKeyboardButton(
                    text="UYKU MODU",
                    callback_data="panel_sleep",
                    icon_custom_emoji_id=emoji.SLEEP,
                    style="success",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="COOKİE DURUMU",
                    callback_data="panel_cookie",
                    icon_custom_emoji_id=emoji.KEY,
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="YASAKLAMA",
                    callback_data="panel_ban",
                    icon_custom_emoji_id=emoji.BAN,
                    style="danger",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="GRUP AYARLARI",
                    callback_data="panel_group_settings",
                    icon_custom_emoji_id=emoji.GROUP_SETTINGS,
                    style="danger",
                ),
                InlineKeyboardButton(
                    text="KAYITLAR",
                    callback_data="panel_records",
                    icon_custom_emoji_id=emoji.DATABASE,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="WEB PANEL",
                    callback_data="panel_web",
                    icon_custom_emoji_id=emoji.WEB,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="GERİ DÖN",
                    callback_data="back_to_start",
                    icon_custom_emoji_id=emoji.REWIND,
                    style="danger",
                ),
            ],
        ]
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#               OYNATICI BİLDİRİM EKRANLARI (NOW PLAYING)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_now_playing_keyboard(url: str) -> InlineKeyboardMarkup:
    """Oynatılıyor ekranı için URL ve kapatma butonları içeren klavye."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Dinle",
                    url=url,
                    icon_custom_emoji_id=emoji.HEADPHONES,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Kanal",
                    url=f"https://t.me/{config.BOT_USERNAME_URL if hasattr(config, 'BOT_USERNAME_URL') else 'HarmonyMusic'}",
                    icon_custom_emoji_id=emoji.MEGAPHONE_PLUS,
                    style="success",
                ),
                InlineKeyboardButton(
                    text="Destek",
                    url=f"https://t.me/{config.BOT_SUPPORT_URL if hasattr(config, 'BOT_SUPPORT_URL') else 'HarmonySupport'}",
                    icon_custom_emoji_id=emoji.SPEECH_BUBBLE,
                    style="success",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Şimdi Oynat",
                    callback_data="skip_now",
                    icon_custom_emoji_id=emoji.ID_AUDIO_BARS,
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Kapat",
                    callback_data="close_msg",
                    icon_custom_emoji_id=emoji.STOP,
                    style="danger",
                ),
            ],
        ]
    )

def get_queue_added_keyboard(url: str = "") -> InlineKeyboardMarkup:
    """Kuyruğa eklendi ekranı için klavye."""
    keyboard = []
    
    if url:
        keyboard.append([
            InlineKeyboardButton(
                text="Dinle",
                url=url,
                icon_custom_emoji_id=emoji.HEADPHONES,
                style="primary",
            ),
        ])
        
    keyboard.append([
        InlineKeyboardButton(
            text="Kanal",
            url=f"https://t.me/{config.BOT_USERNAME_URL if hasattr(config, 'BOT_USERNAME_URL') else 'HarmonyMusic'}",
            icon_custom_emoji_id=emoji.MEGAPHONE_PLUS,
            style="success",
        ),
        InlineKeyboardButton(
            text="Destek",
            url=f"https://t.me/{config.BOT_SUPPORT_URL if hasattr(config, 'BOT_SUPPORT_URL') else 'HarmonySupport'}",
            icon_custom_emoji_id=emoji.SPEECH_BUBBLE,
            style="success",
        ),
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="Şimdi Oynat",
            callback_data="skip_now", # Bu butona basınca sıradaki şarkıya (yani buna) geçer
            icon_custom_emoji_id=emoji.ID_AUDIO_BARS,
            style="primary",
        ),
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="Kapat",
            callback_data="close_msg",
            icon_custom_emoji_id=emoji.STOP,
            style="danger",
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#            YARIŞMA AYARLARI INLINE KLAVYE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_yarisma_keyboard() -> InlineKeyboardMarkup:
    """Yarışma dil ve tür seçimi inline klavyesi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="TÜRKÇE",
                    callback_data="yarisma_tr",
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="İNGİLİZCE",
                    callback_data="yarisma_en",
                    style="primary",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="ARABESK",
                    callback_data="yarisma_arabesk",
                    style="success",
                ),
                InlineKeyboardButton(
                    text="POP",
                    callback_data="yarisma_pop",
                    style="success",
                ),
                InlineKeyboardButton(
                    text="RAP",
                    callback_data="yarisma_rap",
                    style="success",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="KARIŞIK",
                    callback_data="yarisma_mix",
                    icon_custom_emoji_id=emoji.PLAY,
                    style="danger",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="GERİ DÖN",
                    callback_data="back_to_start",
                    icon_custom_emoji_id=emoji.REWIND,
                    style="danger",
                ),
            ],
        ]
    )
