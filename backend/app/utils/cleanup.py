import os
import time

def cleanup_old_files(folder_path: str, max_age_seconds: int = 900):
    """Deletes files older than 15 minutes (900 seconds)."""
    now = time.time()
    if not os.path.exists(folder_path):
        return
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > max_age_seconds:
                os.remove(file_path)