
import sys
import os

# Mevcut dizini ekle
sys.path.append(os.getcwd())

try:
    from services.music import is_spotify_url, get_spotify_metadata
    print("BINGO! Import başarılı.")
    print(f"is_spotify_url: {is_spotify_url}")
    print(f"get_spotify_metadata: {get_spotify_metadata}")
except ImportError as e:
    print(f"HATA! Import başarısız: {e}")
    # Modül listesini kontrol et
    if 'services.music' in sys.modules:
        m = sys.modules['services.music']
        print(f"services.music modülü mevcut. Kaynak: {getattr(m, '__file__', 'bilinmiyor')}")
        print(f"Modüldeki isimler: {dir(m)}")
except Exception as e:
    print(f"Beklenmedik hata: {e}")
