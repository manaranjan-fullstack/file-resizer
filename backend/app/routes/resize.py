import os
import uuid
import tempfile
import traceback
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.services.image_service import resize_image
from app.services.pdf_service import compress_pdf
from app.services.doc_service import compress_docx
from app.utils.cleanup import cleanup_old_files

router = APIRouter()

BASE_TEMP_DIR = os.path.join(tempfile.gettempdir(), "file_resizer_temp")
UPLOAD_DIR = os.path.join(BASE_TEMP_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_TEMP_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.post("/resize")
async def resize_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    quality: int = Form(75),
    scale: float = Form(1.0),
    max_width: Optional[int] = Form(None),
    max_height: Optional[int] = Form(None),
    target_kb: Optional[int] = Form(None)
):
    ext = os.path.splitext(file.filename)[1].lower()
    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    output_filename = f"resized_{file.filename}"
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_{output_filename}")

    with open(input_path, "wb") as f:
        f.write(await file.read())

    try:
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            resize_image(
                input_path, output_path,
                quality=quality, scale=scale,
                max_width=max_width, max_height=max_height,
                target_kb=target_kb
            )
        elif ext == ".pdf":
            compress_pdf(
                input_path, output_path,
                quality=quality, scale=scale,
                target_kb=target_kb
            )
        elif ext == ".docx":
            compress_docx(
                input_path, output_path,
                quality=quality, scale=scale,
                target_kb=target_kb
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")

        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Output file was not generated.")

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

    background_tasks.add_task(cleanup_old_files, OUTPUT_DIR)
    return FileResponse(output_path, filename=output_filename)