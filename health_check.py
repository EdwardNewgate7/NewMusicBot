import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from config import config
from database.db import init_db, get_db
from services.music import validate_cookie_file, search_youtube
from services.userbot import assistant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HealthCheck")

async def check():
    logger.info("--- BOT SAĞLIK KONTROLÜ BAŞLATILDI ---")
    
    # 1. Dizinler
    config.ensure_dirs()
    logger.info(f"✅ Dizinler kontrol edildi: {config.DOWNLOAD_PATH}, {config.DATABASE_PATH}")
    
    # 2. Veritabanı
    try:
        await init_db()
        db = await get_db()
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table';") as cursor:
            tables = await cursor.fetchall()
            logger.info(f"✅ Veritabanı tabloları ({len(tables)} adet): {[t[0] for t in tables]}")
    except Exception as e:
        logger.error(f"❌ Veritabanı hatası: {e}")
    
    # 3. Cookie.txt
    cookie_info = validate_cookie_file()
    if cookie_info["valid"]:
        logger.info(f"✅ Cookie.txt: {cookie_info['message']}")
    else:
        logger.warning(f"⚠️ Cookie.txt: {cookie_info['message']}")
        
    # 4. YouTube Arama Testi
    try:
        results = await search_youtube("tarkan", max_results=1)
        if results:
            logger.info(f"✅ YouTube Arama: Başarılı ({results[0].title})")
        else:
            logger.error("❌ YouTube Arama: Sonuç bulunamadı.")
    except Exception as e:
        logger.error(f"❌ YouTube Arama Hatası: {e}")
        
    # 5. FFmpeg Kontrol
    import shutil
    ffmpeg_path = config.FFMPEG_PATH or shutil.which("ffmpeg")
    if ffmpeg_path:
        logger.info(f"✅ FFmpeg bulundu: {ffmpeg_path}")
    else:
        logger.error("❌ FFmpeg BULUNAMADI! Bot müzik indiremez/dönüştüremez.")
        
    # 6. Asistan Durumu
    logger.info(f"ℹ️ Asistan Durumu: {'AKTİF' if config.ASSISTANT_ENABLED else 'DEVRE DIŞI'}")
    if config.ASSISTANT_ENABLED:
        if config.is_assistant_configured():
            logger.info("✅ Asistan ayarları tam görünüyor.")
        else:
            logger.error("❌ Asistan ayarları eksik!")
            
    logger.info("--- SAĞLIK KONTROLÜ TAMAMLANDI ---")

if __name__ == "__main__":
    asyncio.run(check())
