"""
Harmony Music - Throttle (Flood Koruması) Middleware
Kullanıcıların komutları çok hızlı göndermesini engeller.
"""

from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from config import config


class ThrottleMiddleware(BaseMiddleware):
    """
    Flood koruması middleware'i.
    Her kullanıcı için son komut zamanını takip eder
    ve belirlenen süre dolmadan yeni komut kabul etmez.
    """

    def __init__(self, rate: float | None = None) -> None:
        """
        Args:
            rate: Komutlar arası minimum bekleme süresi (saniye).
                  None ise config'den alınır.
        """
        self.rate = rate or config.THROTTLE_RATE
        self._timestamps: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Kullanıcı ID'sini al
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id is None:
            return await handler(event, data)

        now = time.monotonic()
        last_time = self._timestamps.get(user_id, 0)

        if now - last_time < self.rate:
            # Çok hızlı, görmezden gel
            if isinstance(event, CallbackQuery):
                await event.answer(
                    "⏳ Çok hızlısın! Lütfen biraz bekle.",
                    show_alert=False,
                )
            return None

        self._timestamps[user_id] = now
        return await handler(event, data)


class DatabaseMiddleware(BaseMiddleware):
    """
    Her mesajda kullanıcıyı veritabanına kaydetme middleware'i.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        from database.models import (
            increment_message_count,
            is_user_banned,
            upsert_group,
            upsert_user,
        )

        user = None
        if isinstance(event, Message):
            user = event.from_user
            chat = event.chat
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            chat = event.message.chat if event.message else None

        if user:
            # Yasaklı mı kontrol et
            if await is_user_banned(user.id):
                if isinstance(event, CallbackQuery):
                    await event.answer(
                        "🚫 Bu botu kullanma yetkiniz yok.",
                        show_alert=True,
                    )
                return None

            # Kullanıcıyı kaydet/güncelle
            await upsert_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
            )

            # Grup işlemleri
            if (
                chat
                and chat.type in ("group", "supergroup")
            ):
                await upsert_group(
                    chat_id=chat.id,
                    title=chat.title,
                    added_by=user.id,
                )

                # Mesaj skor sayacını artır (sadece gruplarda)
                if isinstance(event, Message) and not user.is_bot:
                    await increment_message_count(user.id, chat.id)

        return await handler(event, data)
