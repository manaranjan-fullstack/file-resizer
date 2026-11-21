import os
import pymupdf as fitz

def compress_pdf(input_path: str, output_path: str, quality: int = 70, scale: float = 0.75, target_kb: int = None):
    def run_pass(q: int, s: float):
        doc = fitz.open(input_path)
        for page in doc:
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                try:
                    base_image = doc.extract_image(xref)
                    pix = fitz.Pixmap(base_image["image"])
                    if pix.n - pix.alpha >= 4:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    if s < 1.0:
                        new_w = max(50, int(pix.width * s))
                        new_h = max(50, int(pix.height * s))
                        pix = fitz.Pixmap(pix, new_w, new_h)
                    compressed_bytes = pix.tobytes("jpeg", jpg_quality=q)
                    page.replace_image(xref, stream=compressed_bytes)
                except Exception:
                    continue
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

    if target_kb:
        target_bytes = target_kb * 1024
        for s, q in [(0.8, 70), (0.6, 55), (0.45, 40), (0.3, 30), (0.2, 20)]:
            run_pass(q, s)
            if os.path.getsize(output_path) <= target_bytes:
                return
    else:
        run_pass(quality, scale)