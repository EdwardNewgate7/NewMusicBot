"""
Harmony Music - İstatistik ve Skor Middleware'ı
Gelen her mesajı veritabanında puan olarak kaydeder.
"""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from database.models import upsert_user, increment_message_count

logger = logging.getLogger("StatsMiddleware")


class StatsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        # Mesaj bot ile direkt görüşme değilse ve kullanıcı varsa
        if event.from_user and not event.from_user.is_bot:
            user_id = event.from_user.id
            chat_id = event.chat.id
            username = event.from_user.username
            first_name = event.from_user.first_name

            # Arka planda istatistikleri güncelle (Awaited but fast in sqlite)
            try:
                # Kullanıcı son aktiflik ve isim bilgilerini güncelle
                await upsert_user(user_id, username, first_name)
                
                # Mesaj skorlarını (günlük, haftalık, aylık, genel) artır
                await increment_message_count(user_id, chat_id)
            except Exception as e:
                logger.error(f"İstatistik güncelleme hatası: {e}")

        return await handler(event, data)
