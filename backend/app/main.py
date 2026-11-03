from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import os

from app.services.converter import ConversionService

app = FastAPI(title="Black Sugar PDF API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

converter_service = ConversionService()

@app.post("/api/info/pdf")
async def get_pdf_info(file: UploadFile = File(...)):
    try:
        content = await file.read()
        return converter_service.inspect_pdf(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/convert")
async def convert_files(
    files: List[UploadFile] = File(...),
    mode: str = Form(...),
    split_mode: Optional[str] = Form("all_single"),
    ranges_str: Optional[str] = Form(""),
    chunk_size: Optional[int] = Form(2)
):
    try:
        raw_files = []
        for f in files:
            content = await f.read()
            raw_files.append({"filename": f.filename, "content": content})
        
        result = await converter_service.process(
            files=raw_files,
            mode=mode,
            split_mode=split_mode,
            ranges_str=ranges_str,
            chunk_size=chunk_size
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{task_id}")
async def download_file(task_id: str):
    file_path = converter_service.get_download_path(task_id)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="檔案已過期或不存在")
    return FileResponse(file_path, filename=os.path.basename(file_path))

# ================= 託管黑糖饅頭前端靜態頁面 =================
STATIC_DIR = os.path.join(os.path.dirname(__file__), "../static")

if os.path.exists(STATIC_DIR):
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        target = os.path.join(STATIC_DIR, full_path)
        if os.path.exists(target) and os.path.isfile(target):
            return FileResponse(target)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))