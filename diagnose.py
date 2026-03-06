
import sys
import os
import importlib

def check():
    print(f"Python Version: {sys.version}")
    print(f"CWD: {os.getcwd()}")
    print(f"PYTHONPATH: {sys.path}")
    
    try:
        import services.music
        print(f"SUCCESS: 'services.music' imported from {services.music.__file__}")
        
        attrs = dir(services.music)
        needed = ['is_spotify_url', 'get_spotify_metadata']
        for attr in needed:
            if attr in attrs:
                print(f"✅ Found: {attr}")
            else:
                print(f"❌ MISSING: {attr}")
                
        # Try importing specificly
        try:
            from services.music import get_spotify_metadata
            print("✅ from services.music import get_spotify_metadata: SUCCESS")
        except ImportError as e:
            print(f"❌ from services.music import get_spotify_metadata: FAILED ({e})")
            
    except ImportError as e:
        print(f"❌ FAILED to import services.music: {e}")

if __name__ == "__main__":
    check()
