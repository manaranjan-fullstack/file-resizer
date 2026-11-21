import os
import time

def cleanup_old_files(folder_path: str, max_age_seconds: int = 900):
    now = time.time()
    if not os.path.exists(folder_path):
        return
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > max_age_seconds:
                try:
                    os.remove(file_path)
                except Exception:
                    pass