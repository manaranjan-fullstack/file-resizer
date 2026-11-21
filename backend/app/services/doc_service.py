import zipfile
import os
import shutil
from .image_service import resize_image

def compress_docx(input_path: str, output_path: str, quality: int = 70, scale: float = 0.75, target_kb: int = None):
    def run_pass(q: int, s: float):
        temp_dir = input_path + "_extracted"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        media_dir = os.path.join(temp_dir, "word", "media")
        if os.path.exists(media_dir):
            for filename in os.listdir(media_dir):
                file_path = os.path.join(media_dir, filename)
                if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    resize_image(file_path, file_path, quality=q, scale=s)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, temp_dir)
                    zip_out.write(full_path, rel_path)
        shutil.rmtree(temp_dir)

    if target_kb:
        target_bytes = target_kb * 1024
        for s, q in [(0.75, 65), (0.5, 50), (0.35, 35), (0.2, 20), (0.1, 10)]:
            run_pass(q, s)
            if os.path.getsize(output_path) <= target_bytes:
                return
    else:
        run_pass(quality, scale)