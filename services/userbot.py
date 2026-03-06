"""
╔══════════════════════════════════════════════════════════════╗
║        🎵 HARMONY MUSIC - USERBOT VE SES YAYINI ÖZELLİĞİ   ║
║      Asistan hesabı ile grupların sesli sohbetlerine girme   ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import logging

from config import config

# Opsiyonel kütüphaneler (Gerekliyse requirements'den yüklenecek)
try:
    from pyrogram import Client
    from pytgcalls import PyTgCalls
    from pytgcalls import idle, filters
    from pytgcalls.types import Update
    from pytgcalls.types import MediaStream
except ImportError:
    Client = None
    PyTgCalls = None
    MediaStream = None


logger = logging.getLogger("Userbot")

class AssistantClient:
    """Asistan Userbot uygulamasını yönetir."""
    
    def __init__(self):
        self.app = None
        self.call = None
        self.is_started = False
        self._initialize_client()

    def _initialize_client(self):
        """Eğer ayarlar varsa Pyrogram client'ını oluşturur."""
        if not Client or not PyTgCalls:
            return  # Kütüphaneler eksik

        if not config.is_assistant_configured():
            return  # Config eksik
            
        try:
            self.app = Client(
                name="HarmonyAssistant",
                api_id=config.ASSISTANT_API_ID,
                api_hash=config.ASSISTANT_API_HASH,
                session_string=config.ASSISTANT_STRING_SESSION or None,
                phone_number=config.ASSISTANT_PHONE_NUMBER or None,
                in_memory=True,  # Prevent SQLite locking on Railway and container deploys
            )
            self.call = PyTgCalls(self.app)
            
            @self.call.on_update(filters.stream_end)
            async def on_stream_end(client: PyTgCalls, update: Update):
                # Bir müzik bittiğinde kuyruktan (queue.py'deki manager) yenisini oyna
                from services.queue import queue_manager
                import asyncio
                
                chat_id = update.chat_id
                q = queue_manager.get(chat_id)
                
                # Kuyruk bitti mi? Sıradaki var mı bak
                next_item = q.skip()
                if next_item:
                    logger.info(f"Oto-Geçiş (AutoPlay): {chat_id} için {next_item.song.title} başlatılıyor...")
                    # Yeni şarkıya kendiliğinden geç
                    asyncio.create_task(self.play_audio(chat_id, next_item.song.file_path))
                else:
                    # Yeni: Auto-DJ modu aktifse rastgele bir hit çalsın
                    if q.auto_dj:
                        logger.info(f"[{chat_id}] Kuyruk bitti ancak AUTO-DJ devrede. Rastgele şarkı seçiliyor...")
                        asyncio.create_task(self._play_auto_dj(chat_id, q))
                    else:
                        logger.info(f"[{chat_id}] Kuyruk tamamen bitti, yayın durduruldu.")
                        # İsteğe bağlı asistan sohbette uyumasın diye bağlantı kesilebilir
                        asyncio.create_task(self.stop_stream(chat_id))

                
        except Exception as e:
            logger.error(f"Asistan bot client'i oluşturulurken hata: {e}")

    async def _play_auto_dj(self, chat_id: int, q):
        """Auto DJ devredeyse rastgele bir trend şarkı bulur ve çalar."""
        import random
        from services.music import search_youtube, download_song
        from services.queue import QueueItem
        
        fallback_queries = [
            "türkiye trendler 2024", "pop mix türkiye", 
            "arabesk trap mix", "tiktok şarkıları", 
            "yabancı pop hit", "chill lo-fi hip hop"
        ]
        query = random.choice(fallback_queries)
        
        results = await search_youtube(query, max_results=5)
        if not results:
            return
            
        song_result = random.choice(results)
        song = await download_song(song_result.url)
        
        if song and song.file_path:
            # Kuyruğa DJ olarak ekle
            queue_item = QueueItem(
                song=song,
                requested_by=0,
                requested_by_name="🤖 AUTO-DJ"
            )
            q.add(queue_item)
            q.next() # Current'a geçir
            await self.play_audio(chat_id, song.file_path)

    async def start(self):
        """Asistanı ve ses iletişimini başlatır."""
        if not self.app or not self.call:
            if config.is_assistant_configured():
                logger.warning("Asistan ayarlandı ancak 'pyrogram' & 'pytgcalls' kurulu değil.")
            return

        try:
            logger.info("Asistan (Userbot) başlatılıyor...")
            await self.app.start()
            
            # Profil bilgisini alıp loga yazalım
            me = await self.app.get_me()
            logger.info(f"✨ Asistan başarıyla bağlandı! ({me.first_name} | {me.id})")
            
            await self.call.start()
            self.is_started = True
            logger.info("🎵 PyTgCalls (Ses Modülü) aktif edildi!")
            
        except Exception as e:
            logger.error(f"Asistan başlatılamadı: {e}")

    async def stop(self):
        """Güvenli kapanış sağlar."""
        if not self.is_started:
            return

        try:
            logger.info("Asistan (Userbot) kapatılıyor...")
            await self.call.stop()
            await self.app.stop()
            self.is_started = False
        except Exception as e:
            logger.error(f"Asistan kapatılırken hata oluştu: {e}")
            
    async def play_audio(self, chat_id: int, file_path: str, is_video: bool = False):
        """Asistanı ilgili grubun sesli sohbetine bağlayıp belirlenen medyayı oynatmaya başlatır."""
        if not self.is_started or not self.call:
            # Otomatik başlatmayı dene
            try:
                await self.start()
            except Exception:
                return False
                
        if not self.is_started or not self.call:
            return False
            
        try:
            from pytgcalls.types import MediaStream
            logger.info(f"{chat_id} ID'li grubun sesli sohbetinde {'video' if is_video else 'ses'} yayını başlatılıyor...")
            
            # YouTube/Medya linki veya yerel dosya yolu olabilir
            # pytgcalls MediaStream her ikisini de destekler
            
            # Video ayarları
            from pytgcalls.types import AudioQuality, VideoQuality
            
            # MediaStream 2.x+ için ayarlar
            stream = MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p if is_video else None,
                video_flags=(
                    MediaStream.Flags.AUTO_DETECT 
                    if is_video else 
                    MediaStream.Flags.IGNORE
                )
            )
            
            # Sesli sohbete katıl ve yürüt
            try:
                # Grupta olup olmadığını kontrol et (Pyrogram ChatMember)
                try:
                    await self.app.get_chat_member(chat_id, "me")
                except Exception:
                    # Grupta değilse katılmayı dene (Eğer bir link veya username varsa)
                    logger.warning(f"Asistan {chat_id} ID'li grupta bulunamadı, katılım bekleniyor...")
                    # Not: Normalde play() hata verince asistanı manuel gruba davet etmek gerekebilir.
                    # Ancak asistan zaten gruptaysa devam eder.
                    pass

                await self.call.play(chat_id, stream)
                return True
            except Exception as play_err:
                logger.warning(f"Oynatma hatası (%s), asistan sohbete katılıyor olabilir: %s", chat_id, play_err)
                try:
                    # Pytgcalls 2.0+ bazen JOIN_GROUP_CALL_REQUIRED verebilir
                    # Bu durumda play() bazen otomatik katılır bazen hata verir
                    await self.call.play(chat_id, stream)
                    return True
                except Exception as final_err:
                    logger.error("Yayını başlatma tamamen başarısız (%s): %s", chat_id, final_err)
                    return False
            
        except Exception as e:
            logger.error(f"Oynatma hatası ({chat_id}): {e}")
            # Eğer asistan grupta değilse katılmayı dene (opsiyonel)
            return False

    async def pause_stream(self, chat_id: int):
        """Yayını duraklatır."""
        if self.is_started and self.call:
            try:
                await self.call.pause_stream(chat_id)
                return True
            except Exception as e:
                logger.debug(f"Duraklatma hatası {chat_id}: {e}")
        return False

    async def resume_stream(self, chat_id: int):
        """Yayını devam ettirir."""
        if self.is_started and self.call:
            try:
                await self.call.resume_stream(chat_id)
                return True
            except Exception as e:
                logger.debug(f"Devam ettirme hatası {chat_id}: {e}")
        return False

    async def stop_stream(self, chat_id: int):
        """Yayını tamamen durdurur ve aramadan ayrılır."""
        if self.is_started and self.call:
            try:
                # Önce yayını durdur, sonra ayrıl
                try:
                    await self.call.leave_call(chat_id)
                except Exception:
                    pass
                return True
            except Exception as e:
                logger.debug(f"Durdurma hatası {chat_id}: {e}")
        return False

    async def change_volume(self, chat_id: int, volume: int):
        """Ses şiddetini 1 ile 200 arasında değiştirir."""
        if self.is_started and self.call:
            try:
                # 2.x+ sürümlerinde set_volume_call veya change_volume_call
                await self.call.change_volume_call(chat_id, volume)
                return True
            except Exception as e:
                logger.error(f"Sesi değiştirme hatası: {e}")
        return False
        
    async def join_chat(self, chat_link: str):
        """Asistanın bir gruba/kanala katılmasını sağlar."""
        if not self.app or not self.is_started:
            return False
            
        try:
            await self.app.join_chat(chat_link)
            return True
        except Exception as e:
            logger.error(f"Gruba katılma hatası: {e}")
            return False

    async def get_members(self, chat_id: int, limit: int = 100):
        """Gruptaki üyeleri listeler (Asistan aracılığıyla)."""
        if not self.app or not self.is_started:
            return []
            
        try:
            members = []
            async for member in self.app.get_chat_members(chat_id, limit=limit):
                if not member.user.is_bot and not member.user.is_deleted:
                    members.append(member.user)
            return members
        except Exception as e:
            logger.error(f"Üye listesi alma hatası: {e}")
            return []


# Singleton instance
assistant = AssistantClient()
