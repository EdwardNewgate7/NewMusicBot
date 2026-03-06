from dataclasses import dataclass

@dataclass
class SongInfo:
    """İndirilen/bulunan şarkı bilgileri."""
    title: str = ""
    artist: str = ""
    duration: int = 0            # saniye
    url: str = ""                # YouTube URL
    thumbnail: str = ""          # Kapak resmi URL
    file_path: str = ""          # İndirilen dosya yolu
    file_size: int = 0           # Dosya boyutu (byte)
    source: str = "youtube"
    video_id: str = ""           # YouTube video ID
    album: str = ""              # Albüm adı
    upload_date: str = ""        # Yükleme tarihi
    view_count: int = 0          # Görüntülenme sayısı
    like_count: int = 0          # Beğeni sayısı
    channel: str = ""            # Kanal adı
    quality: str = ""            # İndirilen kalite
    is_live: bool = False        # Canlı yayın mı?

@dataclass
class SearchResult:
    """Arama sonucu."""
    title: str = ""
    artist: str = ""
    duration: int = 0
    url: str = ""
    thumbnail: str = ""
    video_id: str = ""
    channel: str = ""
    view_count: int = 0
    upload_date: str = ""
