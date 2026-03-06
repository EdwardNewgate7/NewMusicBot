"""
Harmony Music - Veritabanı Modelleri / Sorgu Fonksiyonları
Tüm CRUD işlemleri burada tanımlanır.
"""

from __future__ import annotations

import datetime
from typing import Any

from database.db import get_db


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     KULLANICI İŞLEMLERİ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def upsert_user(
    user_id: int,
    username: str | None = None,
    first_name: str | None = None,
) -> None:
    """Kullanıcıyı ekler veya günceller."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO users (user_id, username, first_name, last_active)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            username = COALESCE(excluded.username, users.username),
            first_name = COALESCE(excluded.first_name, users.first_name),
            last_active = CURRENT_TIMESTAMP
        """,
        (user_id, username, first_name),
    )
    await db.commit()


async def get_user(user_id: int) -> dict[str, Any] | None:
    """Kullanıcı bilgilerini getirir."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def increment_user_plays(user_id: int) -> None:
    """Kullanıcının toplam dinleme sayısını artırır."""
    db = await get_db()
    await db.execute(
        "UPDATE users SET total_plays = total_plays + 1 WHERE user_id = ?",
        (user_id,),
    )
    await db.commit()


async def is_user_banned(user_id: int) -> bool:
    """Kullanıcının yasaklı olup olmadığını kontrol eder."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT 1 FROM banned_users WHERE user_id = ?", (user_id,)
    )
    return await cursor.fetchone() is not None


async def ban_user(user_id: int, banned_by: int, reason: str = "") -> None:
    """Kullanıcıyı yasaklar."""
    db = await get_db()
    await db.execute(
        """
        INSERT OR REPLACE INTO banned_users (user_id, banned_by, reason)
        VALUES (?, ?, ?)
        """,
        (user_id, banned_by, reason),
    )
    await db.execute(
        "UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,)
    )
    await db.commit()


async def unban_user(user_id: int) -> None:
    """Kullanıcının yasağını kaldırır."""
    db = await get_db()
    await db.execute(
        "DELETE FROM banned_users WHERE user_id = ?", (user_id,)
    )
    await db.execute(
        "UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,)
    )
    await db.commit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                      GRUP İŞLEMLERİ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def upsert_group(
    chat_id: int,
    title: str | None = None,
    added_by: int | None = None,
) -> None:
    """Grubu ekler veya günceller."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO groups (chat_id, title, added_by)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET
            title = COALESCE(excluded.title, groups.title),
            is_active = 1
        """,
        (chat_id, title, added_by),
    )
    await db.commit()


async def get_group(chat_id: int) -> dict[str, Any] | None:
    """Grubun ayarlarını getirir."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM groups WHERE chat_id = ?", (chat_id,)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def update_group_setting(
    chat_id: int, setting: str, value: Any
) -> None:
    """Grup ayarını günceller."""
    db = await get_db()
    # Güvenlik: sadece izin verilen sütunlar
    allowed = {
        "welcome_enabled", "voice_protection", "queue_notify",
        "cleanup_mode", "cover_photo", "play_permission", "is_active",
    }
    if setting not in allowed:
        raise ValueError(f"Geçersiz ayar: {setting}")
    await db.execute(
        f"UPDATE groups SET {setting} = ? WHERE chat_id = ?",
        (value, chat_id),
    )
    await db.commit()


async def get_all_groups() -> list[dict[str, Any]]:
    """Tüm aktif grupları listeler."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM groups WHERE is_active = 1"
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_group_count() -> int:
    """Toplam aktif grup sayısını döndürür."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT COUNT(*) as cnt FROM groups WHERE is_active = 1"
    )
    row = await cursor.fetchone()
    return row["cnt"] if row else 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   ÇALMA LİSTESİ İŞLEMLERİ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def add_to_playlist(
    user_id: int,
    title: str,
    artist: str = "",
    url: str = "",
    duration: int = 0,
) -> int:
    """Çalma listesine şarkı ekler, eklenen ID'yi döndürür."""
    db = await get_db()
    cursor = await db.execute(
        """
        INSERT INTO playlists (user_id, title, artist, url, duration)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, title, artist, url, duration),
    )
    await db.commit()
    return cursor.lastrowid


async def remove_from_playlist(user_id: int, song_id: int) -> bool:
    """Çalma listesinden şarkı siler."""
    db = await get_db()
    cursor = await db.execute(
        "DELETE FROM playlists WHERE id = ? AND user_id = ?",
        (song_id, user_id),
    )
    await db.commit()
    return cursor.rowcount > 0


async def remove_from_playlist_by_title(
    user_id: int, title: str
) -> bool:
    """Şarkı adına göre çalma listesinden siler."""
    db = await get_db()
    cursor = await db.execute(
        "DELETE FROM playlists WHERE user_id = ? AND title LIKE ?",
        (user_id, f"%{title}%"),
    )
    await db.commit()
    return cursor.rowcount > 0


async def get_playlist(user_id: int) -> list[dict[str, Any]]:
    """Kullanıcının çalma listesini getirir."""
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT * FROM playlists
        WHERE user_id = ?
        ORDER BY added_at DESC
        """,
        (user_id,),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_playlist_count(user_id: int) -> int:
    """Kullanıcının çalma listesi şarkı sayısını döndürür."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT COUNT(*) as cnt FROM playlists WHERE user_id = ?",
        (user_id,),
    )
    row = await cursor.fetchone()
    return row["cnt"] if row else 0


async def clear_playlist(user_id: int) -> int:
    """Çalma listesini tamamen siler, silinen şarkı sayısını döndürür."""
    db = await get_db()
    cursor = await db.execute(
        "DELETE FROM playlists WHERE user_id = ?", (user_id,)
    )
    await db.commit()
    return cursor.rowcount


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   DİNLEME GEÇMİŞİ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def add_listen_history(
    user_id: int,
    title: str,
    chat_id: int | None = None,
    artist: str = "",
    url: str = "",
    duration: int = 0,
) -> None:
    """Dinleme geçmişine kayıt ekler."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO listen_history
            (user_id, chat_id, title, artist, url, duration)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, chat_id, title, artist, url, duration),
    )
    await db.commit()


async def get_user_stats(user_id: int) -> dict[str, Any]:
    """Kullanıcının dinleme istatistiklerini getirir."""
    db = await get_db()

    # Toplam dinleme
    cursor = await db.execute(
        "SELECT COUNT(*) as total FROM listen_history WHERE user_id = ?",
        (user_id,),
    )
    total_row = await cursor.fetchone()
    total = total_row["total"] if total_row else 0

    # Bugünkü dinleme
    cursor = await db.execute(
        """
        SELECT COUNT(*) as today FROM listen_history
        WHERE user_id = ? AND DATE(played_at) = DATE('now')
        """,
        (user_id,),
    )
    today_row = await cursor.fetchone()
    today = today_row["today"] if today_row else 0

    # Bu haftaki dinleme
    cursor = await db.execute(
        """
        SELECT COUNT(*) as week FROM listen_history
        WHERE user_id = ?
          AND played_at >= datetime('now', '-7 days')
        """,
        (user_id,),
    )
    week_row = await cursor.fetchone()
    week = week_row["week"] if week_row else 0

    # En çok dinlenen şarkı
    cursor = await db.execute(
        """
        SELECT title, COUNT(*) as cnt FROM listen_history
        WHERE user_id = ?
        GROUP BY title ORDER BY cnt DESC LIMIT 1
        """,
        (user_id,),
    )
    fav_row = await cursor.fetchone()
    fav_song = fav_row["title"] if fav_row else "-"
    fav_count = fav_row["cnt"] if fav_row else 0

    # En çok dinlenen sanatçı
    cursor = await db.execute(
        """
        SELECT artist, COUNT(*) as cnt FROM listen_history
        WHERE user_id = ? AND artist != ''
        GROUP BY artist ORDER BY cnt DESC LIMIT 1
        """,
        (user_id,),
    )
    artist_row = await cursor.fetchone()
    fav_artist = artist_row["artist"] if artist_row else "-"

    return {
        "total_plays": total,
        "today_plays": today,
        "week_plays": week,
        "favorite_song": fav_song,
        "favorite_song_count": fav_count,
        "favorite_artist": fav_artist,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     RUH EŞİ İŞLEMLERİ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def set_soulmate(user_id: int, partner_id: int) -> None:
    """Ruh eşi eşleştirmesi yapar (çift yönlü)."""
    db = await get_db()
    await db.execute(
        "INSERT OR REPLACE INTO soulmates (user_id, partner_id) VALUES (?, ?)",
        (user_id, partner_id),
    )
    await db.execute(
        "INSERT OR REPLACE INTO soulmates (user_id, partner_id) VALUES (?, ?)",
        (partner_id, user_id),
    )
    await db.commit()


async def get_soulmate(user_id: int) -> int | None:
    """Kullanıcının ruh eşini döndürür."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT partner_id FROM soulmates WHERE user_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    return row["partner_id"] if row else None


async def remove_soulmate(user_id: int) -> None:
    """Ruh eşi eşleştirmesini kaldırır (çift yönlü)."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT partner_id FROM soulmates WHERE user_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    if row:
        partner_id = row["partner_id"]
        await db.execute(
            "DELETE FROM soulmates WHERE user_id = ?", (user_id,)
        )
        await db.execute(
            "DELETE FROM soulmates WHERE user_id = ?", (partner_id,)
        )
        await db.commit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                     BOT İSTATİSTİKLERİ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def get_bot_stat(key: str) -> str:
    """Bot istatistik değerini alır."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT value FROM bot_stats WHERE key = ?", (key,)
    )
    row = await cursor.fetchone()
    return row["value"] if row else "0"


async def set_bot_stat(key: str, value: str) -> None:
    """Bot istatistik değerini ayarlar."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO bot_stats (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            updated_at = CURRENT_TIMESTAMP
        """,
        (key, value),
    )
    await db.commit()


async def increment_bot_stat(key: str) -> None:
    """Bot istatistik sayacını artırır."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO bot_stats (key, value, updated_at)
        VALUES (?, '1', CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET
            value = CAST(CAST(value AS INTEGER) + 1 AS TEXT),
            updated_at = CURRENT_TIMESTAMP
        """,
        (key,),
    )
    await db.commit()


async def get_total_user_count() -> int:
    """Toplam kayıtlı kullanıcı sayısını döndürür."""
    db = await get_db()
    cursor = await db.execute("SELECT COUNT(*) as cnt FROM users")
    row = await cursor.fetchone()
    return row["cnt"] if row else 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   MESAJ SKOR SİSTEMİ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def increment_message_count(
    user_id: int, chat_id: int
) -> None:
    """
    Kullanıcının mesaj sayacını tüm periyotlarda artırır.
    (günlük, haftalık, aylık, tüm zamanlar)
    """
    db = await get_db()
    today = datetime.date.today()
    today_str = str(today)
    start_of_week = str(today - datetime.timedelta(days=today.weekday()))
    start_of_month = str(today.replace(day=1))

    # Günlük
    await db.execute(
        """
        INSERT INTO daily_messages (user_id, chat_id, date, count)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(user_id, chat_id, date) DO UPDATE SET
            count = count + 1
        """,
        (user_id, chat_id, today_str),
    )
    # Haftalık
    await db.execute(
        """
        INSERT INTO weekly_messages (user_id, chat_id, week, count)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(user_id, chat_id, week) DO UPDATE SET
            count = count + 1
        """,
        (user_id, chat_id, start_of_week),
    )
    # Aylık
    await db.execute(
        """
        INSERT INTO monthly_messages (user_id, chat_id, month, count)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(user_id, chat_id, month) DO UPDATE SET
            count = count + 1
        """,
        (user_id, chat_id, start_of_month),
    )
    # Tüm zamanlar
    await db.execute(
        """
        INSERT INTO alltime_messages (user_id, chat_id, count)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, chat_id) DO UPDATE SET
            count = count + 1
        """,
        (user_id, chat_id),
    )
    await db.commit()


async def get_leaderboard(
    chat_id: int,
    period: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Belirtilen periyot için liderlik tablosunu getirir.
    period: 'daily', 'weekly', 'monthly', 'alltime'
    """
    db = await get_db()
    today = datetime.date.today()

    if period == "daily":
        table = "daily_messages"
        where = "chat_id = ? AND date = ?"
        params = (chat_id, str(today))
    elif period == "weekly":
        table = "weekly_messages"
        start_of_week = str(today - datetime.timedelta(days=today.weekday()))
        where = "chat_id = ? AND week = ?"
        params = (chat_id, start_of_week)
    elif period == "monthly":
        table = "monthly_messages"
        start_of_month = str(today.replace(day=1))
        where = "chat_id = ? AND month = ?"
        params = (chat_id, start_of_month)
    else:  # alltime
        table = "alltime_messages"
        where = "chat_id = ?"
        params = (chat_id,)

    cursor = await db.execute(
        f"""
        SELECT user_id, count FROM {table}
        WHERE {where}
        ORDER BY count DESC
        LIMIT ?
        """,
        (*params, limit),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_user_message_stats(
    user_id: int, chat_id: int
) -> dict[str, int]:
    """Kullanıcının belirli bir gruptaki mesaj istatistiklerini getirir."""
    db = await get_db()
    today = datetime.date.today()

    # Günlük
    cursor = await db.execute(
        "SELECT count FROM daily_messages WHERE user_id=? AND chat_id=? AND date=?",
        (user_id, chat_id, str(today)),
    )
    row = await cursor.fetchone()
    daily = row["count"] if row else 0

    # Haftalık
    start_of_week = str(today - datetime.timedelta(days=today.weekday()))
    cursor = await db.execute(
        "SELECT count FROM weekly_messages WHERE user_id=? AND chat_id=? AND week=?",
        (user_id, chat_id, start_of_week),
    )
    row = await cursor.fetchone()
    weekly = row["count"] if row else 0

    # Aylık
    start_of_month = str(today.replace(day=1))
    cursor = await db.execute(
        "SELECT count FROM monthly_messages WHERE user_id=? AND chat_id=? AND month=?",
        (user_id, chat_id, start_of_month),
    )
    row = await cursor.fetchone()
    monthly = row["count"] if row else 0

    # Tüm zamanlar
    cursor = await db.execute(
        "SELECT count FROM alltime_messages WHERE user_id=? AND chat_id=?",
        (user_id, chat_id),
    )
    row = await cursor.fetchone()
    alltime = row["count"] if row else 0

    return {
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
        "alltime": alltime,
    }


async def get_user_rank(
    chat_id: int, period: str, user_id: int
) -> int:
    """Kullanıcının belirli periyottaki sıralamasını getirir."""
    db = await get_db()
    today = datetime.date.today()

    if period == "daily":
        table = "daily_messages"
        where = "chat_id = ? AND date = ?"
        params = (chat_id, str(today))
    elif period == "weekly":
        table = "weekly_messages"
        start_of_week = str(today - datetime.timedelta(days=today.weekday()))
        where = "chat_id = ? AND week = ?"
        params = (chat_id, start_of_week)
    elif period == "monthly":
        table = "monthly_messages"
        start_of_month = str(today.replace(day=1))
        where = "chat_id = ? AND month = ?"
        params = (chat_id, start_of_month)
    else:
        table = "alltime_messages"
        where = "chat_id = ?"
        params = (chat_id,)

    # Kullanıcının sayısını al
    cursor = await db.execute(
        f"SELECT count FROM {table} WHERE {where} AND user_id = ?",
        (*params, user_id),
    )
    row = await cursor.fetchone()
    if not row:
        return 0

    user_count = row["count"]

    # Daha yüksek sayıda olanları say
    cursor = await db.execute(
        f"SELECT COUNT(*) as rank FROM {table} WHERE {where} AND count > ?",
        (*params, user_count),
    )
    rank_row = await cursor.fetchone()
    return (rank_row["rank"] if rank_row else 0) + 1


async def get_group_message_stats(chat_id: int) -> dict[str, Any]:
    """Grubun mesaj istatistiklerini döndürür."""
    db = await get_db()
    today = datetime.date.today()

    # Günlük
    cursor = await db.execute(
        "SELECT COUNT(DISTINCT user_id) as users, SUM(count) as total FROM daily_messages WHERE chat_id=? AND date=?",
        (chat_id, str(today)),
    )
    row = await cursor.fetchone()
    daily_users = row["users"] if row else 0
    daily_total = row["total"] if row and row["total"] else 0

    # Haftalık
    start_of_week = str(today - datetime.timedelta(days=today.weekday()))
    cursor = await db.execute(
        "SELECT COUNT(DISTINCT user_id) as users, SUM(count) as total FROM weekly_messages WHERE chat_id=? AND week=?",
        (chat_id, start_of_week),
    )
    row = await cursor.fetchone()
    weekly_users = row["users"] if row else 0
    weekly_total = row["total"] if row and row["total"] else 0

    # Aylık
    start_of_month = str(today.replace(day=1))
    cursor = await db.execute(
        "SELECT COUNT(DISTINCT user_id) as users, SUM(count) as total FROM monthly_messages WHERE chat_id=? AND month=?",
        (chat_id, start_of_month),
    )
    row = await cursor.fetchone()
    monthly_users = row["users"] if row else 0
    monthly_total = row["total"] if row and row["total"] else 0

    return {
        "daily_users": daily_users, "daily_total": int(daily_total),
        "weekly_users": weekly_users, "weekly_total": int(weekly_total),
        "monthly_users": monthly_users, "monthly_total": int(monthly_total),
    }


async def cleanup_old_scores() -> None:
    """Eski skor verilerini temizler (7+ gün günlük, 4+ hafta haftalık, 3+ ay aylık)."""
    db = await get_db()
    today = datetime.date.today()

    seven_days_ago = str(today - datetime.timedelta(days=7))
    await db.execute(
        "DELETE FROM daily_messages WHERE date < ?", (seven_days_ago,)
    )

    four_weeks_ago = str(today - datetime.timedelta(weeks=4))
    await db.execute(
        "DELETE FROM weekly_messages WHERE week < ?", (four_weeks_ago,)
    )

    three_months_ago = str(today - datetime.timedelta(days=90))
    await db.execute(
        "DELETE FROM monthly_messages WHERE month < ?", (three_months_ago,)
    )
    await db.commit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                 HOŞ GELDİN AYARLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def get_welcome_enabled(chat_id: int) -> bool:
    """Grubun hoş geldin mesajı aktif mi kontrol eder."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT welcome_enabled FROM groups WHERE chat_id = ?",
        (chat_id,),
    )
    row = await cursor.fetchone()
    return bool(row["welcome_enabled"]) if row else True


async def set_welcome_enabled(chat_id: int, enabled: bool) -> None:
    """Grubun hoş geldin mesajını açar/kapatır."""
    await update_group_setting(chat_id, "welcome_enabled", int(enabled))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                  DUYURU / BROADCAST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def get_all_chat_ids() -> list[int]:
    """Tüm aktif grup ID'lerini döndürür."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT chat_id FROM groups WHERE is_active = 1"
    )
    rows = await cursor.fetchall()
    return [row["chat_id"] for row in rows]


async def get_all_user_ids() -> list[int]:
    """Tüm kayıtlı ve yasaklı olmayan kullanıcı ID'lerini döndürür."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT user_id FROM users WHERE is_banned = 0"
    )
    rows = await cursor.fetchall()
    return [row["user_id"] for row in rows]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#           DİNLEME GEÇMİŞİ & TREND SORGULARI (v3.0)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def get_listen_history(
    user_id: int, limit: int = 10
) -> list[dict[str, Any]]:
    """
    Kullanıcının son dinleme geçmişini getirir.
    listen_history tablosundan en son dinlenenleri çeker.
    """
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT title, artist, url, duration, played_at
        FROM listen_history
        WHERE user_id = ?
        ORDER BY played_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_top_songs(limit: int = 10) -> list[dict[str, Any]]:
    """
    Botun veritabanındaki en çok dinlenen şarkıları getirir.
    Tüm kullanıcıların dinleme geçmişinden toplu sayım.
    """
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT title, artist, COUNT(*) as count
        FROM listen_history
        GROUP BY title
        ORDER BY count DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]

