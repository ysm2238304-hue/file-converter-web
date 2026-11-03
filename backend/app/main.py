import os
import uuid
import shutil
import zipfile
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.utils.security import sanitize_filename, clean_expired_tasks
from app.services.pdf_engine import (
    get_pdf_page_count, merge_pdfs, split_pdf, safe_pdf_to_jpg, safe_jpg_to_pdf
)
from app.services.office_engine import pdf_to_word_converter, word_to_pdf_libreoffice

app = FastAPI(title="DocuMorph API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_UPLOAD_DIR = os.path.abspath("tasks")
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

@app.post("/api/info/pdf")
async def inspect_pdf(file: UploadFile = File(...)):
    """輕量端點：快速讀取上傳 PDF 的總頁數"""
    task_id = uuid.uuid4().hex
    temp_dir = os.path.join(BASE_UPLOAD_DIR, task_id)
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, sanitize_filename(file.filename))

    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        info = get_pdf_page_count(temp_file)
        return info
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/api/convert")
async def execute_conversion(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    mode: str = Form(...),
    split_mode: Optional[str] = Form("all_single"),
    ranges_str: Optional[str] = Form(""),
    chunk_size: Optional[int] = Form(2),
):
    """核心轉檔端點"""
    background_tasks.add_task(clean_expired_tasks, BASE_UPLOAD_DIR)

    task_id = uuid.uuid4().hex
    task_dir = os.path.join(BASE_UPLOAD_DIR, task_id)
    input_dir = os.path.join(task_dir, "input")
    output_dir = os.path.join(task_dir, "output")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    saved_files = []
    for f in files:
        safe_name = sanitize_filename(f.filename)
        dest_path = os.path.join(input_dir, safe_name)
        with open(dest_path, "wb") as buf:
            shutil.copyfileobj(f.file, buf)
        saved_files.append(dest_path)

    output_files = []

    try:
        if mode == "merge_pdf":
            out_pdf = os.path.join(output_dir, "合併完成文件.pdf")
            cnt = merge_pdfs(saved_files, out_pdf)
            if cnt == 0:
                raise HTTPException(status_code=400, detail="沒有檔案被成功合併")
            output_files.append(out_pdf)

        elif mode == "split_pdf":
            out_list = split_pdf(
                saved_files[0], output_dir, mode=split_mode, ranges_str=ranges_str, chunk_size=chunk_size
            )
            output_files.extend(out_list)

        elif mode == "pdf_to_jpg":
            for f in saved_files:
                imgs = safe_pdf_to_jpg(f, output_dir)
                output_files.extend(imgs)

        elif mode == "jpg_to_pdf":
            out_pdf = os.path.join(output_dir, "圖片合併.pdf")
            if safe_jpg_to_pdf(saved_files, out_pdf):
                output_files.append(out_pdf)
            else:
                raise HTTPException(status_code=400, detail="圖片轉 PDF 失敗")

        elif mode == "pdf_to_word":
            for f in saved_files:
                base = os.path.splitext(os.path.basename(f))[0]
                out_docx = os.path.join(output_dir, f"{base}.docx")
                pdf_to_word_converter(f, out_docx)
                output_files.append(out_docx)

        elif mode == "word_to_pdf":
            for f in saved_files:
                out_pdf = word_to_pdf_libreoffice(f, output_dir)
                output_files.append(out_pdf)

        else:
            raise HTTPException(status_code=400, detail=f"不支援的轉檔模式: {mode}")

    except Exception as e:
        shutil.rmtree(task_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))

    if len(output_files) == 1:
        download_name = os.path.basename(output_files[0])
        final_path = output_files[0]
    else:
        zip_path = os.path.join(task_dir, "轉換成果打包.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for f in output_files:
                z.write(f, arcname=os.path.basename(f))
        download_name = "轉換成果打包.zip"
        final_path = zip_path

    return {
        "status": "success",
        "task_id": task_id,
        "filename": download_name,
        "download_url": f"/api/download/{task_id}?filename={download_name}"
    }

@app.get("/api/download/{task_id}")
async def download_task_file(task_id: str, filename: str):
    """下載產出的檔案"""
    target_dir = os.path.join(BASE_UPLOAD_DIR, task_id)
    if not os.path.exists(target_dir):
        raise HTTPException(status_code=404, detail="任務不存在或已過期")

    for root, _, files in os.walk(target_dir):
        if filename in files:
            return FileResponse(
                os.path.join(root, filename),
                filename=filename,
                media_type="application/octet-stream"
            )
    raise HTTPException(status_code=404, detail="找不到指定下載檔案")
