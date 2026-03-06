"""
╔══════════════════════════════════════════════════════════════╗
║       🎵 HARMONY MUSIC - Merkezi Yapılandırma v3.0         ║
║  Ortam değişkenlerini (.env) güvenli ve düzenli yönetir.     ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

# Projenin kök dizini (config.py'nin bulunduğu klasör)
BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Tüm bot yapılandırmalarının bulunduğu veri sınıfı."""

    BASE_DIR: Path = BASE_DIR

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #             1. TELEGRAM BOT AYARLARI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8621616338:AAFgwh6tyOUnJmQSIhPBMSqYFbVqNSCEt4c")
    
    # Virgülle ayrılmış ID'leri listeye çevir (örn: "123,456" -> [123, 456])
    OWNER_IDS: list[int] = [
        int(uid.strip())
        for uid in os.getenv("OWNER_IDS", "8548853828").split(",")
        if uid.strip().isdigit()
    ]

    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "@HarmonySongMusic_bot")
    BOT_NAME: str = os.getenv("BOT_NAME", "Harmony Music Bot")

    DEV_USERNAME: str = os.getenv("DEV_USERNAME", "@ZeusYardimix")
    DEV2_USERNAME: str = os.getenv("DEV2_USERNAME", "@Qu1iyef")

    # Botun log bildirimleri atacağı grup (Kişi ID, Grup ID vs. olabilir)
    LOGGER_ID: int = int(os.getenv("LOGGER_ID", "-1002247653245")) # Example default, should be configured in .env


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #             2. ASİSTAN (USERBOT) AYARLARI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    ASSISTANT_BOT_USERNAME: str = os.getenv("ASSISTANT_BOT_USERNAME", "@HarmonySongMusic")
    
    ASSISTANT_ENABLED: bool = os.getenv("ASSISTANT_ENABLED", "false").lower() in ("true", "1", "yes")
    ASSISTANT_API_ID: int = int(os.getenv("ASSISTANT_API_ID") or "38168684")
    ASSISTANT_API_HASH: str = os.getenv("ASSISTANT_API_HASH", "e29dd7af9cac399bfbc003a4c60a23b6")
    ASSISTANT_PHONE_NUMBER: str = os.getenv("ASSISTANT_PHONE_NUMBER", "+905053348251")
    ASSISTANT_STRING_SESSION: str = os.getenv("ASSISTANT_STRING_SESSION", "BAJGaGwAYciIig2KL3K2mHmkeCXPWM26JRyUYtolXtcGgTDgxKztLiOQk5Bx4bJJNAm5J8ZFVd4RVeGe5Cc6cepOsZvYkHOFuQheB74j7ZPneDrdFyitgj3PZ-8UBK6OVWivA6ZMbqsMKWD1OJThgsNbIJyDtmn-4XjicjvXAmTP4XZxxq-97hKpDKS68_Fxk8rlANVAKlv1Q1wvjRJqTUineylIoc3MEjkwWkfDpYqr5hKdCfB25hGW4W04Gg5JLcw0QIP8m1Qk6RDfi5jc8v41RE70XBqGWwl4cnb0tJxiPpJ_fbtJ4FxFV1vXpqTkfltQBZMaLIDAN2OdQ0WL3IaVIV_6-wAAAAH8BwLoAA")


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #             3. YOL VE DİZİN AYARLARI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "harmony_music.db"))
    DOWNLOAD_PATH: str = os.getenv("DOWNLOAD_PATH", str(BASE_DIR / "downloads"))
    
    # Eğer özel bir klasöre kuruluysa FFMPEG yolu (örn: C:\ffmpeg\bin\ffmpeg.exe)
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "")


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #             4. MEDYA VE KALİTE AYARLARI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Kalite ve Format
    AUDIO_QUALITY: str = os.getenv("AUDIO_QUALITY", "320")  # "64", "128", "192", "256", "320"
    AUDIO_FORMAT: str = os.getenv("AUDIO_FORMAT", "mp3")    # "mp3", "m4a", "opus", "flac"
    VIDEO_QUALITY: str = os.getenv("VIDEO_QUALITY", "720")  # "360", "480", "720", "1080"


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #             5. LİMİTLER VE QUOTA AYARLARI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # Dosya boyutu ve süre sınırları
    MAX_SONG_DURATION: int = int(os.getenv("MAX_SONG_DURATION") or "600")  # Saniye bazında (örn 10 dk)
    
    # 50 MB limits
    MAX_AUDIO_FILE_SIZE: int = int(os.getenv("MAX_AUDIO_FILE_SIZE") or str(50 * 1024 * 1024))
    MAX_VIDEO_FILE_SIZE: int = int(os.getenv("MAX_VIDEO_FILE_SIZE") or str(50 * 1024 * 1024))

    # Kuyruk ve Liste sınırları
    MAX_PLAYLIST_SIZE: int = int(os.getenv("MAX_PLAYLIST_SIZE") or "50")
    MAX_QUEUE_SIZE: int = int(os.getenv("MAX_QUEUE_SIZE") or "25")
    AUTO_CLEANUP_SECONDS: int = int(os.getenv("AUTO_CLEANUP_SECONDS") or "3600")
    THROTTLE_RATE: float = float(os.getenv("THROTTLE_RATE") or "2")


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #             6. YOUTUBE VE YTDLP AYARLARI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # Arama sonuç sayısı
    DEFAULT_SEARCH_RESULTS: int = int(os.getenv("DEFAULT_SEARCH_RESULTS") or "5")
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS") or "10")
    
    # Cookie (Yaş/bölge kısıtlı videoları aşmak için)
    COOKIE_FILE: str = os.getenv("COOKIE_FILE", str(BASE_DIR / "cookie.txt"))
    COOKIE_URL: str = os.getenv("COOKIE_URL", "https://batbin.me/conjugated")
    COOKIE_ENABLED: bool = os.getenv("COOKIE_ENABLED", "true").lower() in ("true", "1", "yes")

    # yt-dlp ağ ayarları
    YTDLP_GEO_BYPASS: bool = os.getenv("YTDLP_GEO_BYPASS", "true").lower() in ("true", "1", "yes")
    YTDLP_SOCKET_TIMEOUT: int = int(os.getenv("YTDLP_SOCKET_TIMEOUT") or "30")
    YTDLP_RETRIES: int = int(os.getenv("YTDLP_RETRIES") or "3")
    YTDLP_USER_AGENT: str = os.getenv(
        "YTDLP_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #             7. DİĞER MODÜL AYARLARI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    DEFAULT_WELCOME_ENABLED: bool = os.getenv("DEFAULT_WELCOME_ENABLED", "true").lower() in ("true", "1", "yes")
    DEFAULT_RADIO_URL: str = os.getenv("DEFAULT_RADIO_URL", "https://listen.powerapp.com.tr/powerfm/mpeg/icecast.audio")
    GENIUS_API_TOKEN: str = os.getenv("GENIUS_API_TOKEN", "")


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #             METOTLAR VE YARDIMCI FONKSİYONLAR
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @classmethod
    def is_assistant_configured(cls) -> bool:
        """Asistan hesabının (Userbot) bağlantı bilgileri tam mı?"""
        return (
            cls.ASSISTANT_ENABLED
            and cls.ASSISTANT_API_ID > 0
            and bool(cls.ASSISTANT_API_HASH)
        )

    @classmethod
    def get_cookie_path(cls) -> str | None:
        """Cookie dosyası kullanıma uygun ise tam yolunu verir, değilse None döner."""
        if not cls.COOKIE_ENABLED:
            return None
        
        cookie_path = Path(cls.COOKIE_FILE)

        # Eğer COOKIE_URL tanımlanmışsa ve yerel dosya yok/eskiyse URL'den çek (Yarım saatte bir)
        if cls.COOKIE_URL:
            import time
            import urllib.request
            import logging
            
            try:
                if not cookie_path.exists() or (time.time() - cookie_path.stat().st_mtime > 1800):
                    cookie_url = cls.COOKIE_URL
                    if "batbin.me" in cookie_url and "/raw/" not in cookie_url:
                        cookie_url = cookie_url.replace("batbin.me/", "batbin.me/raw/")
                        
                    req = urllib.request.Request(cookie_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as response:
                        content = response.read().decode('utf-8')
                        # Check if it looks like HTML
                        if "<!DOCTYPE" in content or "<html" in content:
                            logging.getLogger("Config").error(f"Cookie URL'den indirilirken geçersiz içerik (HTML) algılandı: {cookie_url}")
                        else:
                            cookie_path.write_text(content, encoding='utf-8')
                            logging.getLogger("Config").info(f"Cookie dosyası güncellendi (URL): {cookie_url}")
            except Exception as e:
                logging.getLogger("Config").error(f"Cookie URL'den indirilirken hata oluştu: {e}")

        if cookie_path.exists() and cookie_path.stat().st_size > 0:
            return str(cookie_path)
        return None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #             6. BAN KORUMASI VE STABİLİTE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    YTDLP_USER_AGENTS: list[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
    ]

    @classmethod
    def get_random_user_agent(cls) -> str:
        import random
        return random.choice(cls.YTDLP_USER_AGENTS)

    @classmethod
    def get_base_ytdlp_opts(cls) -> dict:
        """YouTube-DL / Yt-Dlp modülü için temel indirme argümanlarını üretir."""
        opts: dict = {
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True,
            "noprogress": True,
            "cachedir": False,  # Turbo: Ön bellek dosyası oluşturma
            "concurrent_fragment_downloads": 10,  # Turbo: 10 kat daha hızlı indirme
            "socket_timeout": cls.YTDLP_SOCKET_TIMEOUT,
            "retries": cls.YTDLP_RETRIES,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios", "web", "mweb", "android_music"],
                },
            },
            "check_formats": False,  # Hız ve stabilite için format kontrolünü atla
            "nocheckcertificate": True,
            "source_address": "0.0.0.0",
            "force_ipv4": True,
            "http_headers": {
                "User-Agent": cls.get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Sec-Fetch-Mode": "navigate",
            },
        }

        if cls.YTDLP_GEO_BYPASS:
            opts["geo_bypass"] = True

        cookie_path = cls.get_cookie_path()
        if cookie_path:
            opts["cookiefile"] = cookie_path

        if cls.FFMPEG_PATH:
            opts["ffmpeg_location"] = cls.FFMPEG_PATH

        return opts

    @classmethod
    def ensure_dirs(cls) -> None:
        """Bot başlatıldığında gereken zorunlu işletim sistemi dizinlerini garantiler."""
        Path(cls.DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)
        Path(cls.DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
        (BASE_DIR / "cache").mkdir(parents=True, exist_ok=True)
        (BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)


# Tüm uygulamada kullanılacak Config kopyesi

