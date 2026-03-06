"""
Harmony Music - Şarkı Kuyruk Yönetimi Servisi
Her grup (chat) için ayrı kuyruk, thread-safe.
"""

from __future__ import annotations

import asyncio
import random
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from services.types import SongInfo


@dataclass
class QueueItem:
    """Kuyruktaki bir şarkı öğesi."""
    song: SongInfo
    requested_by: int            # Kullanıcı ID
    requested_by_name: str = ""  # Kullanıcı adı


class ChatQueue:
    """Bir grubun şarkı kuyruğu."""

    def __init__(self, chat_id: int) -> None:
        self.chat_id = chat_id
        self._queue: deque[QueueItem] = deque()
        self._current: QueueItem | None = None
        self._is_playing: bool = False
        self._is_paused: bool = False
        self._loop_mode: str = "off"  # off, one, all
        self._started_at: float = 0.0
        self._total_paused_time: float = 0.0
        self._last_pause_time: float = 0.0
        self._auto_dj: bool = False  # Auto-DJ Modu

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def current(self) -> QueueItem | None:
        return self._current

    @property
    def loop_mode(self) -> str:
        return self._loop_mode

    @property
    def auto_dj(self) -> bool:
        return self._auto_dj

    def set_auto_dj(self, state: bool) -> None:
        """Auto-DJ modunu ayarlar."""
        self._auto_dj = state

    def set_loop(self, mode: str) -> None:
        """Tekrar modunu ayarlar: 'off', 'one', 'all'."""
        if mode in ("off", "one", "all"):
            self._loop_mode = mode

    def add(self, item: QueueItem) -> int:
        """Kuyruğa şarkı ekler, kuyruk pozisyonunu döndürür."""
        self._queue.append(item)
        return len(self._queue)

    def next(self) -> QueueItem | None:
        """Sıradaki şarkıyı alır ve current olarak ayarlar."""
        import time
        if self._loop_mode == "one" and self._current:
            self._started_at = time.time()
            self._total_paused_time = 0.0
            return self._current
            
        if self._loop_mode == "all" and self._current:
            self._queue.append(self._current)

        if not self._queue:
            self._current = None
            self._is_playing = False
            self._started_at = 0.0
            return None

        self._current = self._queue.popleft()
        self._is_playing = True
        self._is_paused = False
        self._started_at = time.time()
        self._total_paused_time = 0.0
        return self._current

    def skip(self) -> QueueItem | None:
        """Mevcut şarkıyı atlar, sıradakine geçer."""
        # Loop one modunda bile atla
        old_loop = self._loop_mode
        if self._loop_mode == "one":
            self._loop_mode = "all"
        result = self.next()
        if old_loop == "one":
            self._loop_mode = old_loop
        return result

    def pause(self) -> None:
        """Çalmayı duraklatır."""
        import time
        if not self._is_paused:
            self._is_paused = True
            self._last_pause_time = time.time()

    def resume(self) -> None:
        """Çalmaya devam eder."""
        import time
        if self._is_paused:
            self._is_paused = False
            if self._last_pause_time > 0:
                self._total_paused_time += (time.time() - self._last_pause_time)
                self._last_pause_time = 0.0

    def get_progress(self) -> float:
        """Şu anki şarkının kaç saniyedir çaldığını hesaplar."""
        import time
        if not self._current or not self._is_playing:
            return 0.0
            
        if self._is_paused:
            p_time = self._last_pause_time if self._last_pause_time > 0 else time.time()
            total_active = p_time - self._started_at - self._total_paused_time
        else:
            total_active = time.time() - self._started_at - self._total_paused_time
            
        return max(0.0, total_active)

    def stop(self) -> None:
        """Çalmayı tamamen durdurur ve kuyruğu temizler."""
        self._queue.clear()
        self._current = None
        self._is_playing = False
        self._is_paused = False
        self._loop_mode = "off"

    def remove(self, index: int) -> QueueItem | None:
        """Belirli indeksteki şarkıyı kuyruktan çıkarır (0-indexed)."""
        if 0 <= index < len(self._queue):
            item = self._queue[index]
            del self._queue[index]
            return item
        return None

    def shuffle(self) -> None:
        """Kuyruğu karıştırır."""
        items = list(self._queue)
        random.shuffle(items)
        self._queue = deque(items)

    def get_list(self) -> list[QueueItem]:
        """Kuyrukun kopyasını liste olarak döndürür."""
        return list(self._queue)

    @property
    def size(self) -> int:
        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0


class QueueManager:
    """
    Global kuyruk yöneticisi.
    Her chat_id için ayrı ChatQueue tutar.
    """

    def __init__(self) -> None:
        self._queues: dict[int, ChatQueue] = {}

    def get(self, chat_id: int) -> ChatQueue:
        """Grubun kuyruğunu döndürür, yoksa oluşturur."""
        if chat_id not in self._queues:
            self._queues[chat_id] = ChatQueue(chat_id)
        return self._queues[chat_id]

    def remove(self, chat_id: int) -> None:
        """Grubun kuyruğunu siler."""
        self._queues.pop(chat_id, None)

    def get_active_chats(self) -> list[int]:
        """Aktif müzik çalan grupların listesini döndürür."""
        return [
            cid for cid, q in self._queues.items()
            if q.is_playing
        ]

    def get_total_playing(self) -> int:
        """Toplam aktif çalan grup sayısını döndürür."""
        return sum(1 for q in self._queues.values() if q.is_playing)


# Singleton kuyruk yöneticisi
queue_manager = QueueManager()
