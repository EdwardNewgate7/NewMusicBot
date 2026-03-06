import os
import sys
import asyncio
import logging
import urllib.request
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Fixer")

def check_ffmpeg_presence():
    import shutil
    # Path'de var mı?
    found = shutil.which("ffmpeg")
    if found:
        return found
    
    # Yaygın Windows yolları
    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        r"C:\yt-dlp\ffmpeg.exe",
        os.path.join(os.getcwd(), "ffmpeg.exe")
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p
    return None

async def force_fix():
    logger.info("--- BOT OTOMATİK DÜZELTME BAŞLATILDI ---")
    
    # 1. Cookie.txt İndirme (Batbin veya başka bir yerden)
    # Eğer .env'de boşsa default'u dene
    cookie_url = config.COOKIE_URL or "https://batbin.me/conjugated"
    try:
        cookie_path = Path("cookie.txt")
        logger.info(f"Cookie indiriliyor: {cookie_url}")
        req = urllib.request.Request(cookie_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')
            cookie_path.write_text(content, encoding='utf-8')
            logger.info("✅ Cookie.txt başarıyla indirildi ve kaydedildi.")
    except Exception as e:
        logger.error(f"❌ Cookie indirme hatası: {e}")

    # 2. FFmpeg Kontrol ve .env'ye yazma eğer bulunursa
    ffmpeg_path = check_ffmpeg_presence()
    if ffmpeg_path:
        logger.info(f"✅ FFmpeg bulundu: {ffmpeg_path}")
    else:
        logger.warning("⚠️ FFmpeg bulunamadı. Lütfen kurun veya proje klasörüne ffmpeg.exe atın.")

    # 3. Dizinleri kontrol et
    config.ensure_dirs()
    logger.info("✅ downloads, data, cache, logs dizinleri kontrol edildi.")

    logger.info("--- DÜZELTME TAMAMLANDI ---")

if __name__ == "__main__":
    asyncio.run(force_fix())
