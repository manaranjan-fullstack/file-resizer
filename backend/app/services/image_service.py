import os
from PIL import Image

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
        # Convert RGBA/Palette to RGB if saving as JPEG
        if img.mode in ("RGBA", "P") and output_path.lower().endswith((".jpg", ".jpeg")):
            img = img.convert("RGB")

        # 1. Apply explicit max width/height (preserving aspect ratio)
        if max_width or max_height:
            w, h = img.size
            ratio = min(
                (max_width / w) if max_width else 1.0,
                (max_height / h) if max_height else 1.0
            )
            if ratio < 1.0:
                img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)

        # 2. Apply percentage scale
        elif scale < 1.0:
            new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # 3. If Target KB is specified, iteratively find the best quality & scale
        if target_kb:
            target_bytes = target_kb * 1024
            current_img = img.copy()

            for _ in range(5):  # Up to 5 dimension-reduction passes if needed
                low, high = 15, 95
                best_quality = 15

                while low <= high:
                    mid = (low + high) // 2
                    current_img.save(output_path, optimize=True, quality=mid)
                    if os.path.getsize(output_path) <= target_bytes:
                        best_quality = mid
                        low = mid + 1
                    else:
                        high = mid - 1

                current_img.save(output_path, optimize=True, quality=best_quality)
                if os.path.getsize(output_path) <= target_bytes:
                    return

                # Still larger than target_kb -> shrink dimensions by 20% and retry
                new_w = max(100, int(current_img.width * 0.8))
                new_h = max(100, int(current_img.height * 0.8))
                current_img = current_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            img.save(output_path, optimize=True, quality=quality)