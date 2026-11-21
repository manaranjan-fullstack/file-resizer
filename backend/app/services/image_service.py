import os
from PIL import Image

def save_with_quality(img: Image.Image, output_path: str, quality: int):
    ext = os.path.splitext(output_path)[1].lower()
    if ext == ".png":
        colors = max(8, int((quality / 100) * 256))
        quantized = img.convert("RGBA").quantize(colors=colors, method=Image.Quantize.FASTOCTREE)
        quantized.save(output_path, optimize=True)
    else:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(output_path, optimize=True, quality=quality)

def resize_image(
    input_path: str,
    output_path: str,
    quality: int = 75,
    scale: float = 1.0,
    max_width: int = None,
    max_height: int = None,
    target_kb: int = None
):
    with Image.open(input_path) as img:
        if max_width or max_height:
            w, h = img.size
            ratio = min(
                (max_width / w) if max_width else 1.0,
                (max_height / h) if max_height else 1.0
            )
            if ratio < 1.0:
                img = img.resize((max(1, int(w * ratio)), max(1, int(h * ratio))), Image.Resampling.LANCZOS)
        elif scale < 1.0:
            new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        if target_kb:
            target_bytes = target_kb * 1024
            current_img = img.copy()

            for _ in range(12):
                low, high = 5, 95
                best_quality = 5

                while low <= high:
                    mid = (low + high) // 2
                    save_with_quality(current_img, output_path, mid)
                    if os.path.getsize(output_path) <= target_bytes:
                        best_quality = mid
                        low = mid + 1
                    else:
                        high = mid - 1

                save_with_quality(current_img, output_path, best_quality)
                if os.path.getsize(output_path) <= target_bytes:
                    return

                if current_img.width <= 24 or current_img.height <= 24:
                    break

                new_w = max(24, int(current_img.width * 0.75))
                new_h = max(24, int(current_img.height * 0.75))
                current_img = current_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            save_with_quality(img, output_path, quality)