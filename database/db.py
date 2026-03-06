"""
Harmony Music - SQLite Veritabanı Bağlantısı
Asenkron SQLite bağlantısı ve tablo oluşturma.
"""

import aiosqlite
import logging

from config import config

logger = logging.getLogger("HarmonyDB")

# Global veritabanı bağlantısı
_db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    """Aktif veritabanı bağlantısını döndürür."""
    global _db
    if _db is None:
        raise RuntimeError("Veritabanı henüz başlatılmadı! init_db() çağırın.")
    return _db


async def init_db() -> None:
    """
    Veritabanını başlatır ve tabloları oluşturur.
    Bot başlangıcında bir kez çağrılır.
    """
    global _db

    config.ensure_dirs()

    _db = await aiosqlite.connect(config.DATABASE_PATH)
    _db.row_factory = aiosqlite.Row

    # WAL modu - daha iyi performans
    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute("PRAGMA foreign_keys=ON")

    # ── Tablolar ───────────────────────────────────────────────
    await _db.executescript("""
        -- Kullanıcılar
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY,
            username      TEXT,
            first_name    TEXT,
            language      TEXT DEFAULT 'tr',
            joined_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_plays   INTEGER DEFAULT 0,
            is_banned     INTEGER DEFAULT 0
        );

        -- Gruplar
        CREATE TABLE IF NOT EXISTS groups (
            chat_id          INTEGER PRIMARY KEY,
            title            TEXT,
            added_by         INTEGER,
            joined_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active        INTEGER DEFAULT 1,
            welcome_enabled  INTEGER DEFAULT 1,
            voice_protection INTEGER DEFAULT 0,
            queue_notify     INTEGER DEFAULT 1,
            cleanup_mode     INTEGER DEFAULT 0,
            cover_photo      INTEGER DEFAULT 1,
            play_permission  TEXT DEFAULT 'all'
        );

        -- Çalma Listeleri (Kullanıcı Başına)
        CREATE TABLE IF NOT EXISTS playlists (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT NOT NULL,
            artist      TEXT DEFAULT '',
            url         TEXT DEFAULT '',
            duration    INTEGER DEFAULT 0,
            added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            play_count  INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        -- Dinleme Geçmişi
        CREATE TABLE IF NOT EXISTS listen_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            chat_id     INTEGER,
            title       TEXT NOT NULL,
            artist      TEXT DEFAULT '',
            url         TEXT DEFAULT '',
            duration    INTEGER DEFAULT 0,
            played_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        -- Ruh Eşleri
        CREATE TABLE IF NOT EXISTS soulmates (
            user_id     INTEGER NOT NULL,
            partner_id  INTEGER NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (partner_id) REFERENCES users(user_id)
        );

        -- Yasaklı Kullanıcılar (Bot seviyesinde)
        CREATE TABLE IF NOT EXISTS banned_users (
            user_id     INTEGER PRIMARY KEY,
            banned_by   INTEGER,
            reason      TEXT DEFAULT '',
            banned_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Bot İstatistikleri
        CREATE TABLE IF NOT EXISTS bot_stats (
            key         TEXT PRIMARY KEY,
            value       TEXT DEFAULT '0',
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Grup Zamanlayıcıları
        CREATE TABLE IF NOT EXISTS timers (
            chat_id     INTEGER PRIMARY KEY,
            stop_at     TIMESTAMP,
            close_voice INTEGER DEFAULT 0,
            set_by      INTEGER,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Mesaj Skor Sistemi: Günlük
        CREATE TABLE IF NOT EXISTS daily_messages (
            user_id     INTEGER NOT NULL,
            chat_id     INTEGER NOT NULL,
            date        TEXT NOT NULL,
            count       INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, chat_id, date)
        );

        -- Mesaj Skor Sistemi: Haftalık
        CREATE TABLE IF NOT EXISTS weekly_messages (
            user_id     INTEGER NOT NULL,
            chat_id     INTEGER NOT NULL,
            week        TEXT NOT NULL,
            count       INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, chat_id, week)
        );

        -- Mesaj Skor Sistemi: Aylık
        CREATE TABLE IF NOT EXISTS monthly_messages (
            user_id     INTEGER NOT NULL,
            chat_id     INTEGER NOT NULL,
            month       TEXT NOT NULL,
            count       INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, chat_id, month)
        );

        -- Mesaj Skor Sistemi: Tüm Zamanlar
        CREATE TABLE IF NOT EXISTS alltime_messages (
            user_id     INTEGER NOT NULL,
            chat_id     INTEGER NOT NULL,
            count       INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, chat_id)
        );

        -- İndeksleri oluştur
        CREATE INDEX IF NOT EXISTS idx_playlists_user
            ON playlists(user_id);
        CREATE INDEX IF NOT EXISTS idx_history_user
            ON listen_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_history_date
            ON listen_history(played_at);
        CREATE INDEX IF NOT EXISTS idx_daily_chat
            ON daily_messages(chat_id, date);
        CREATE INDEX IF NOT EXISTS idx_weekly_chat
            ON weekly_messages(chat_id, week);
        CREATE INDEX IF NOT EXISTS idx_monthly_chat
            ON monthly_messages(chat_id, month);
        CREATE INDEX IF NOT EXISTS idx_alltime_chat
            ON alltime_messages(chat_id);
    """)

    await _db.commit()
    logger.info(f"✅ Veritabanı başlatıldı: {config.DATABASE_PATH}")


async def close_db() -> None:
    """Veritabanı bağlantısını kapatır."""
    global _db
    if _db:
        await _db.close()
        _db = None
        logger.info("🔴 Veritabanı bağlantısı kapatıldı.")
