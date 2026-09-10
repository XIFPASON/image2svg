import os
from pathlib import Path
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError
import uuid

from ..core.config import ALLOWED_IMAGE_SUFFIXES, new_output_path, new_upload_path
from ..core.fast_converter import FastConverter
from .models import ConversionResponse

app = FastAPI(title="Bitmap to SVG Converter API")

MAX_UPLOAD_BYTES = int(os.environ.get("IMAGE2SVG_MAX_UPLOAD_BYTES", 20 * 1024 * 1024))
tasks: dict[str, dict[str, str]] = {}


def process_image(task_id: str, input_path: Path, output_path: Path) -> None:
    try:
        FastConverter().convert(str(input_path), str(output_path))
        tasks[task_id] = {"status": "completed", "output_path": str(output_path)}
    except Exception as e:
        tasks[task_id] = {"status": "failed", "message": str(e)}
    finally:
        input_path.unlink(missing_ok=True)

@app.post("/convert", response_model=ConversionResponse)
async def convert_image(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_IMAGE_SUFFIXES:
        raise HTTPException(status_code=415, detail="Only PNG and JPEG images are supported.")

    task_id = str(uuid.uuid4())
    input_path = new_upload_path(file.filename or "")
    output_path = new_output_path()
    size = 0
    with input_path.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                input_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail=f"Upload must be smaller than {MAX_UPLOAD_BYTES} bytes.")
            buffer.write(chunk)
    await file.close()

    try:
        with Image.open(input_path) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        input_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="The uploaded file is not a valid image.")

    tasks[task_id] = {"status": "processing", "output_path": str(output_path)}
    background_tasks.add_task(process_image, task_id, input_path, output_path)
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Image conversion started in background.",
        "output_url": f"/result/{task_id}"
    }

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Unknown task.")
    if task["status"] == "failed":
        return {"status": "failed", "message": task["message"]}
    output_path = Path(task["output_path"])
    if task["status"] == "completed" and output_path.exists():
        return FileResponse(output_path, media_type="image/svg+xml", filename="converted.svg")
    return {"status": "processing", "message": "File is still being converted."}
