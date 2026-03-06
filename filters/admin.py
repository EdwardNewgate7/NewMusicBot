"""
Harmony Music - Admin / Owner Filtreleri
Komutları yalnızca yetkili kullanıcıların çalıştırmasını sağlar.
"""

from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import config


class IsOwner(BaseFilter):
    """
    Mesajı gönderenin bot sahibi olup olmadığını kontrol eder.
    OWNER_IDS listesindeki kullanıcılar için True döner.
    """

    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        return message.from_user.id in config.OWNER_IDS


class IsAdmin(BaseFilter):
    """
    Mesajı gönderenin grup yöneticisi veya sahibi olup olmadığını
    kontrol eder.
    """

    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        # Bot sahibi her zaman admin
        if message.from_user.id in config.OWNER_IDS:
            return True

        # Özel sohbette herkes admin
        if message.chat.type == "private":
            return True

        # Grup kontrolü
        try:
            member = await message.chat.get_member(message.from_user.id)
            return member.status in ("creator", "administrator")
        except Exception:
            return False


class IsGroup(BaseFilter):
    """Mesajın bir gruptan gelip gelmediğini kontrol eder."""

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in ("group", "supergroup")


class IsPrivate(BaseFilter):
    """Mesajın özel sohbetten gelip gelmediğini kontrol eder."""

    async def __call__(self, message: Message) -> bool:
        return message.chat.type == "private"
