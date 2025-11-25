from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from ..core.live_main import LIVEConverter
from .models import ConversionResponse

app = FastAPI(title="Bitmap to SVG Converter API")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

converter = LIVEConverter()

def process_image(task_id: str, input_path: str, output_path: str):
    try:
        converter.convert(input_path, output_path)
        print(f"Task {task_id} completed.")
    except Exception as e:
        print(f"Task {task_id} failed: {e}")

@app.post("/convert", response_model=ConversionResponse)
async def convert_image(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{task_id}_{file.filename}")
    output_path = os.path.join(OUTPUT_DIR, f"{task_id}.svg")
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    background_tasks.add_task(process_image, task_id, input_path, output_path)
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Image conversion started in background.",
        "output_url": f"/result/{task_id}"
    }

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    output_path = os.path.join(OUTPUT_DIR, f"{task_id}.svg")
    if os.path.exists(output_path):
        return FileResponse(output_path, media_type="image/svg+xml")
    return {"status": "processing", "message": "File not ready or does not exist."}
