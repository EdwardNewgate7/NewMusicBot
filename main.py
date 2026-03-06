"""
╔══════════════════════════════════════════════════════════════╗
║              🎵 HARMONY MUSIC v3.0.0 🎵                  ║
║                                                              ║
║  Telegram'ın en güçlü ve hızlı müzik asistanı.              ║
║  aiogram 3.25+ ile geliştirilmiştir.                         ║
║                                                              ║
║  v3.0 Yenilikler:                                            ║
║  • Cookie.txt ile YouTube yaş/bölge kısıtlama bypass        ║
║  • 320kbps yüksek kaliteli ses indirme                       ║
║  • Gelişmiş arama (sonuç seçimi ile)                         ║
║  • Şarkı sözleri bulma (/sozler)                             ║
║  • Tekrar modu (tek/liste) (/loop)                           ║
║  • Kuyruk karıştırma (/karistir)                             ║
║  • Şu an çalan (/calan, /np)                                 ║
║  • Kalite bilgisi (/kalite)                                  ║
║  • Cookie durumu kontrol (/cookie)                           ║
║  • SoundCloud platform desteği                               ║
║  • SQLite veritabanı (çalma listeleri, istatistikler)        ║
║  • YouTube müzik arama & indirme (yt-dlp)                    ║
║  • Şarkı kuyruğu yönetimi                                   ║
║  • Çoklu platform medya indirici                             ║
║  • Inline mod (şarkı arama)                                  ║
║  • Flood koruması & veritabanı middleware                     ║
║  • Admin/Owner filtreleri                                    ║
║  • Otomatik dosya temizleme                                  ║
║  • Bot komutları otomatik kayıt                              ║
╚══════════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter

import config as bot_config
config = bot_config.config
from database.db import close_db, init_db
from middlewares.throttle import DatabaseMiddleware, ThrottleMiddleware

# ── Router'ları İçe Aktar ──────────────────────────────────────
from routers import (
    admin,
    broadcast,
    callbacks,
    fun,
    inline,
    media_detector,
    music,
    playlist,
    scorer,
    start,
    welcome,
)

async def set_bot_commands(bot: Bot) -> None:
    """
    Bot komutlarını Telegram'a kaydeder.
    Kullanıcılar / yazınca komut listesini görebilir.
    """
    # ── Özel sohbet komutları ──────────────────────────────────
    private_commands = [
        BotCommand(command="start", description="🚀 Başlat / Start"),
        BotCommand(command="help", description="❓ Yardım / Help"),
        BotCommand(command="playlist", description="📋 Listem / Playlist"),
        BotCommand(command="indir", description="📥 İndir / Download"),
        BotCommand(command="stat", description="📊 İstatistik / Stats"),
        BotCommand(command="gecmis", description="🕒 Geçmiş / History"),
        BotCommand(command="trend", description="🔥 Trendler / Trends"),
        BotCommand(command="radyo", description="📻 Radyo / Radio"),
        BotCommand(command="hakkinda", description="ℹ️ Hakkında / About"),
    ]
    await bot.set_my_commands(private_commands)

    # ── Grup komutları ─────────────────────────────────────────
    group_commands = [
        # --- Temel Müzik ---
        BotCommand(command="oynat", description="🎵 Şarkı çal / Play"),
        BotCommand(command="voynat", description="🎬 Video çal / VPlay"),
        BotCommand(command="ara", description="🔍 Ara / Search"),
        BotCommand(command="durdur", description="⏸ Durdur / Pause"),
        BotCommand(command="devam", description="▶️ Devam / Resume"),
        BotCommand(command="atla", description="⏭ Atla / Skip"),
        BotCommand(command="son", description="⏹ Bitir / Stop"),
        # --- Listeler ---
        BotCommand(command="sira", description="📋 Kuyruk / Queue"),
        BotCommand(command="calan", description="🎧 Çalan / NP"),
        BotCommand(command="playlist", description="📀 Listem / Playlist"),
        BotCommand(command="gecmis", description="🕒 Geçmiş / History"),
        # --- Ayarlar & Skor ---
        BotCommand(command="top", description="🏆 Sıralama / Top"),
        BotCommand(command="stat", description="📊 Skor / Stats"),
        BotCommand(command="loop", description="🔁 Tekrar / Loop"),
        BotCommand(command="karistir", description="🔀 Karıştır / Shuffle"),
        BotCommand(command="sozler", description="📝 Sözler / Lyrics"),
        BotCommand(command="ses", description="📶 Ses / Volume"),
        BotCommand(command="ayarlar", description="⚙️ Ayarlar / Settings"),
        BotCommand(command="tag", description="📢 Etiket / Mention"),
        BotCommand(command="sabitle", description="📌 Mesajı / Sabitle"),
        BotCommand(command="kaldir", description="📌 Sabiti / Kaldır"),
        BotCommand(command="sor", description="🔮 Sihirli Top / 8ball"),
        BotCommand(command="askmetre", description="💖 Aşk Ölçer / Love"),
    ]
    await bot.set_my_commands(
        group_commands,
        scope=BotCommandScopeAllGroupChats(),
    )


async def on_startup(bot: Bot) -> None:
    """Bot başlangıcında çalışan fonksiyon."""
    logger = logging.getLogger("HarmonyMusicBot")

    # FFmpeg kontrolü
    import shutil
    ffmpeg_cmd = config.FFMPEG_PATH or "ffmpeg"
    if shutil.which(ffmpeg_cmd):
        logger.info(f"✅ FFmpeg aktif: {shutil.which(ffmpeg_cmd)}")
    else:
        logger.error("❌ FFmpeg BULUNAMADI! İndirmeler ve ses akışı çalışmayabilir.")

    # Veritabanını başlat
    await init_db()
    logger.info("✅ Veritabanı başlatıldı.")

    # Bot komutlarını kaydet
    await set_bot_commands(bot)
    logger.info("✅ Bot komutları Telegram'a kaydedildi.")

    # Dizinleri oluştur
    config.ensure_dirs()
    logger.info("✅ Gerekli dizinler oluşturuldu.")

    # Asistanı başlat (Aktif edildiyse ve kuruluysa)
    from services.userbot import assistant
    if config.ASSISTANT_ENABLED:
        await assistant.start()

    # Cookie.txt durumunu kontrol et
    from services.music import validate_cookie_file
    cookie_info = validate_cookie_file()
    if cookie_info["valid"]:
        logger.info(f"🍪 Cookie.txt aktif: {cookie_info['message']}")
    else:
        logger.warning(f"⚠️ Cookie.txt: {cookie_info['message']}")


async def on_shutdown(bot: Bot) -> None:
    """Bot kapanırken çalışan fonksiyon."""
    logger = logging.getLogger("HarmonyMusicBot")

    # Veritabanını kapat
    await close_db()
    logger.info("🔴 Veritabanı kapatıldı.")

    # Asistanı kapat
    from services.userbot import assistant
    if assistant.is_started:
        await assistant.stop()

    # İndirme dosyalarını temizle
    from services.music import clean_old_downloads
    cleaned = clean_old_downloads()
    if cleaned:
        logger.info(f"🗑️ {cleaned} geçici dosya temizlendi.")


async def periodic_cleanup() -> None:
    """Periyodik dosya + skor temizleme görevi."""
    from services.music import clean_old_downloads
    from database.models import cleanup_old_scores

    while True:
        await asyncio.sleep(1800)  # Her 30 dakikada bir
        clean_old_downloads()
        await cleanup_old_scores()


async def main() -> None:
    """Botun ana giriş fonksiyonu."""

    # Dizinleri en başta garanti et
    config.ensure_dirs()
    
    # FFmpeg yolunu PATH'e ekle (pytgcalls'ın bulabilmesi için)
    if config.FFMPEG_PATH:
        ffmpeg_bin = str(Path(config.FFMPEG_PATH).parent)
        if ffmpeg_bin not in os.environ["PATH"]:
            os.environ["PATH"] = f"{ffmpeg_bin}{os.pathsep}{os.environ['PATH']}"
            
    log_file = config.BASE_DIR / "logs" / "bot.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s  │  %(levelname)-8s  │  "
            "%(name)s  │  %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    logger = logging.getLogger("HarmonyMusicBot")

    # ── Token Kontrolü ─────────────────────────────────────────
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "❌ BOT_TOKEN bulunamadı! "
            "Lütfen .env dosyasına geçerli bir token ekleyin."
        )
        sys.exit(1)

    # ── Bot Nesnesi ────────────────────────────────────────────
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )

    # ── Dispatcher ─────────────────────────────────────────────
    dp = Dispatcher()

    # ── Middleware'leri Kaydet ──────────────────────────────────
    dp.message.middleware(ThrottleMiddleware())
    dp.callback_query.middleware(ThrottleMiddleware(rate=1.0))
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    # ── Router'ları Kaydet ─────────────────────────────────────
    dp.include_routers(
        start.router,           # /start komutu
        callbacks.router,       # Callback query handler'ları
        music.router,           # Müzik oynatma komutları
        playlist.router,        # Çalma listesi komutları
        admin.router,           # Yönetici komutları
        scorer.router,          # Mesaj skor sistemi
        welcome.router,         # Hoş geldin sistemi
        fun.router,             # Eğlence komutları
        broadcast.router,       # Duyuru sistemi
        inline.router,          # Inline şarkı arama
        media_detector.router,  # Otomatik medya link tespiti
    )

    # ── Startup / Shutdown Hook'ları ───────────────────────────
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # ── Hata Yakalayıcı ────────────────────────────────────────
    @dp.errors(ExceptionTypeFilter(TelegramBadRequest))
    async def global_error_handler(update, exception):
        if "message is not modified" in str(exception.message):
            return True
        logger.error(f"TelegramBadRequest: {exception}", exc_info=False)
        return True

    # ── Cookie durumu ──────────────────────────────────────────
    cookie_status = "✅ AKTİF" if config.get_cookie_path() else "❌ YOK"

    # ── Başlangıç Mesajı ──────────────────────────────────────
    logger.info("━" * 55)
    logger.info("🎵 HARMONY MUSIC v3.0.0 BAŞLATILIYOR...")
    logger.info("━" * 55)
    logger.info(f"  Bot Adı    : {config.BOT_NAME}")
    logger.info(f"  Kullanıcı  : {config.BOT_USERNAME}")
    logger.info(f"  Sahip IDs  : {config.OWNER_IDS}")
    logger.info(f"  Veritabanı : {config.DATABASE_PATH}")
    logger.info(f"  İndirmeler : {config.DOWNLOAD_PATH}")
    logger.info(f"  Maks.Süre  : {config.MAX_SONG_DURATION}s")
    logger.info(f"  Throttle   : {config.THROTTLE_RATE}s")
    logger.info("━" * 55)
    logger.info(f"  🍪 Cookie  : {cookie_status}")
    logger.info(f"  🎚 Kalite  : {config.AUDIO_QUALITY}kbps {config.AUDIO_FORMAT.upper()}")
    logger.info(f"  🎬 Video   : {config.VIDEO_QUALITY}p")
    logger.info(f"  📦 Maks.Boy: {config.MAX_AUDIO_FILE_SIZE // (1024*1024)}MB")
    logger.info("━" * 55)

    # ── Eski güncellemeleri atla ve polling başlat ─────────────
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Bot başarıyla başlatıldı! Polling dinleniyor...")

        # Periyodik temizleme görevini arka planda başlat
        cleanup_task = asyncio.create_task(periodic_cleanup())

        await dp.start_polling(bot)

        # Temizleme görevini iptal et
        cleanup_task.cancel()

    finally:
        logger.info("🔴 Bot kapatılıyor...")
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🔴 Bot kullanıcı tarafından durduruldu.")

