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
                        new_w = max(16, int(pix.width * s))
                        new_h = max(16, int(pix.height * s))
                        pix = fitz.Pixmap(pix, new_w, new_h)
                    compressed_bytes = pix.tobytes("jpeg", jpg_quality=q)
                    page.replace_image(xref, stream=compressed_bytes)
                except Exception:
                    continue
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

    def rasterize_pdf(dpi: int, q: int):
        src = fitz.open(input_path)
        out = fitz.open()
        for page in src:
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("jpeg", jpg_quality=q)
            new_page = out.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(page.rect, stream=img_bytes)
        out.save(output_path, garbage=4, deflate=True, clean=True)
        src.close()
        out.close()

    if target_kb:
        target_bytes = target_kb * 1024
        for s, q in [(0.75, 65), (0.5, 50), (0.35, 35), (0.2, 20), (0.1, 10)]:
            run_pass(q, s)
            if os.path.getsize(output_path) <= target_bytes:
                return

        for dpi, q in [(72, 35), (50, 25), (36, 15), (24, 10)]:
            rasterize_pdf(dpi, q)
            if os.path.getsize(output_path) <= target_bytes:
                return
    else:
        run_pass(quality, scale)