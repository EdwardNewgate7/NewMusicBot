try:
    from services.music import get_download_file_count
    print("Import successful!")
    count = get_download_file_count()
    print(f"File count: {count}")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
