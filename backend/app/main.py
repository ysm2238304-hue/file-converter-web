import os
import io
import json
import uuid
import shutil
import zipfile
from typing import List, Optional

import fitz  # PyMuPDF
from PIL import Image, ImageOps
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_SUPPORTED = True
except ImportError:
    HEIF_SUPPORTED = False

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.utils.security import sanitize_filename, clean_expired_tasks
from app.services.pdf_engine import (
    get_pdf_page_count, merge_pdfs, split_pdf, safe_pdf_to_jpg, safe_jpg_to_pdf
)
from app.services.office_engine import pdf_to_word_converter, word_to_pdf_libreoffice

app = FastAPI(title="DocuMorph API", version="2.4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_UPLOAD_DIR = os.path.abspath("tasks")
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

# 照片批次處理安全上限 (保護 Render 記憶體與避免逾時)
MAX_IMAGE_BATCH_COUNT = 20
MAX_IMAGE_BATCH_BYTES = 50 * 1024 * 1024  # 50 MB


# ======================== 極限畫質壓縮與轉檔核心函式 ========================
def _render_and_compress_pdf(src_doc, output_path: str, dpi: int, quality: int, keep_color: bool):
    """使用 PyMuPDF 渲染頁面並交由 Pillow 進行 4:2:0 JPEG 極限壓縮"""
    new_doc = fitz.open()
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    colorspace = fitz.csRGB if keep_color else fitz.csGRAY
    mode_str = "RGB" if keep_color else "L"

    try:
        for page in src_doc:
            pix = page.get_pixmap(matrix=mat, colorspace=colorspace, alpha=False)
            img = Image.frombytes(mode_str, [pix.width, pix.height], pix.samples)
            pix = None  # 立即釋放記憶體，避免雲端環境 OOM

            buf = io.BytesIO()
            img.save(
                buf,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True,
                subsampling=2,
            )
            img.close()
            img_bytes = buf.getvalue()

            rect = page.rect
            new_page = new_doc.new_page(width=rect.width, height=rect.height)
            new_page.insert_image(rect, stream=img_bytes)

        new_doc.save(
            output_path,
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
            clean=True,
        )
    finally:
        new_doc.close()


def compress_pdf_extreme(
    input_path: str,
    output_path: str,
    preset: str = "auto",
    target_mb: float = 4.5,
    manual_dpi: int = 75,
    manual_quality: int = 20,
    keep_color: bool = True,
):
    """依預設策略或自訂參數執行 PDF 極限壓縮"""
    orig_bytes = os.path.getsize(input_path)
    target_bytes = max(0.1, float(target_mb)) * 1024 * 1024

    preset_map = {
        "extreme": [{"dpi": 60, "quality": 12}],
        "strong": [{"dpi": 75, "quality": 20}],
        "medium": [{"dpi": 95, "quality": 30}],
        "custom": [{
            "dpi": max(40, min(200, int(manual_dpi))),
            "quality": max(5, min(95, int(manual_quality))),
        }],
    }

    if preset in preset_map:
        profiles = preset_map[preset]
    else:
        profiles = [
            {"dpi": 95, "quality": 30},
            {"dpi": 80, "quality": 20},
            {"dpi": 68, "quality": 15},
            {"dpi": 55, "quality": 10},
        ]

    src_doc = fitz.open(input_path)
    try:
        for prof in profiles:
            _render_and_compress_pdf(
                src_doc,
                output_path=output_path,
                dpi=prof["dpi"],
                quality=prof["quality"],
                keep_color=keep_color,
            )
            out_bytes = os.path.getsize(output_path)
            if out_bytes <= target_bytes and out_bytes < orig_bytes:
                break
    finally:
        src_doc.close()


def _prepare_rgb_image(img: Image.Image) -> Image.Image:
    """修正手機 EXIF 旋轉方向並統一轉為 RGB 模式"""
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        alpha = img.convert("RGBA")
        bg = Image.new("RGBA", alpha.size, (255, 255, 255))
        img = Image.alpha_composite(bg, alpha).convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")
    return img


def compress_single_image(
    input_path: str,
    output_dir: str,
    max_dimension: int = 1024,
    quality: int = 25,
    out_format: str = "JPEG",
) -> str:
    """將單張照片（含 HEIC）縮放並以高壓縮率輸出為 JPEG 或 WebP"""
    max_dim = max(300, min(4000, int(max_dimension)))
    q = max(5, min(95, int(quality)))
    file_name = os.path.basename(input_path)
    base, _ = os.path.splitext(file_name)

    with Image.open(input_path) as raw_img:
        img = _prepare_rgb_image(raw_img)
        w, h = img.size
        max_side = max(w, h)
        if max_side > max_dim:
            scale = max_dim / float(max_side)
            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

        if out_format.upper() == "WEBP":
            out_path = os.path.join(output_dir, f"{base}_compressed.webp")
            img.save(out_path, format="WEBP", quality=q, method=6)
        else:
            out_path = os.path.join(output_dir, f"{base}_compressed.jpg")
            img.save(
                out_path,
                format="JPEG",
                quality=q,
                optimize=True,
                progressive=True,
                subsampling=2,
            )
        img.close()

    return out_path


def convert_heic_to_jpg(input_path: str, output_dir: str, quality: int = 92) -> str:
    """將單張 HEIC/HEIF 照片轉正方向並快速轉存為高畫質 JPG"""
    if not HEIF_SUPPORTED:
        raise RuntimeError("伺服器尚未安裝 pillow-heif，無法讀取 HEIC 檔案")

    q = max(50, min(100, int(quality)))
    file_name = os.path.basename(input_path)
    base, _ = os.path.splitext(file_name)
    out_path = os.path.join(output_dir, f"{base}.jpg")

    with Image.open(input_path) as raw_img:
        img = _prepare_rgb_image(raw_img)
        img.save(
            out_path,
            format="JPEG",
            quality=q,
            optimize=True,
            progressive=True,
        )
        img.close()

    return out_path


def organize_pdf_pages(input_path: str, output_path: str, page_ops_json: str):
    """依使用者指定的頁序與旋轉角度重組 PDF（未包含的頁面即視為刪除）"""
    try:
        ops = json.loads(page_ops_json or "[]")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="頁面操作參數格式錯誤")

    if not isinstance(ops, list) or len(ops) == 0:
        raise HTTPException(status_code=400, detail="請至少保留一頁 PDF")

    src_doc = fitz.open(input_path)
    out_doc = fitz.open()
    try:
        total = len(src_doc)
        for item in ops:
            p_num = int(item.get("page", 0))
            rot = int(item.get("rotate", 0)) % 360
            p_idx = p_num - 1
            if 0 <= p_idx < total:
                out_doc.insert_pdf(src_doc, from_page=p_idx, to_page=p_idx)
                if rot != 0:
                    page = out_doc[-1]
                    page.set_rotation((page.rotation + rot) % 360)

        if len(out_doc) == 0:
            raise HTTPException(status_code=400, detail="沒有有效的頁面可輸出")

        out_doc.save(output_path, garbage=4, deflate=True)
    finally:
        out_doc.close()
        src_doc.close()


def protect_or_unlock_pdf(input_path: str, output_path: str, action: str, password: str):
    """使用 PyMuPDF 進行 AES-256 加密或解除密碼"""
    pw = (password or "").strip()
    if not pw:
        raise HTTPException(status_code=400, detail="請輸入 PDF 密碼")

    doc = fitz.open(input_path)
    try:
        if action == "encrypt":
            if doc.needs_pass:
                raise HTTPException(status_code=400, detail="此 PDF 已有密碼保護，請先解除密碼後再重新加密")
            doc.save(
                output_path,
                encryption=fitz.PDF_ENCRYPT_AES_256,
                user_pw=pw,
                owner_pw=pw,
                garbage=4,
                deflate=True,
            )
        elif action == "unlock":
            if doc.needs_pass:
                if not doc.authenticate(pw):
                    raise HTTPException(status_code=400, detail="密碼錯誤，無法解除保護")
            doc.save(
                output_path,
                encryption=fitz.PDF_ENCRYPT_NONE,
                garbage=4,
                deflate=True,
            )
        else:
            raise HTTPException(status_code=400, detail="不支援的安全操作模式")
    finally:
        doc.close()


def images_to_a4_pdf(
    image_paths: List[str],
    output_path: str,
    layout: str = "2_up",
    orientation: str = "portrait",
):
    """將多張照片（含 HEIC）自動等比例置中排版進標準 A4 PDF"""
    if orientation == "landscape":
        page_w, page_h = 841.89, 595.28
    else:
        page_w, page_h = 595.28, 841.89

    if layout == "1_up":
        cols, rows = 1, 1
    elif layout == "4_up":
        cols, rows = 2, 2
    else:
        cols, rows = (2, 1) if orientation == "landscape" else (1, 2)

    per_page = cols * rows
    margin = 24.0
    gap = 14.0
    cell_w = (page_w - 2 * margin - (cols - 1) * gap) / cols
    cell_h = (page_h - 2 * margin - (rows - 1) * gap) / rows

    doc = fitz.open()
    try:
        current_page = None
        for idx, img_path in enumerate(image_paths):
            slot = idx % per_page
            if slot == 0:
                current_page = doc.new_page(width=page_w, height=page_h)

            col = slot % cols
            row = slot // cols
            x0 = margin + col * (cell_w + gap)
            y0 = margin + row * (cell_h + gap)

            with Image.open(img_path) as raw_img:
                img = _prepare_rgb_image(raw_img)
                w, h = img.size
                if max(w, h) > 1600:
                    scale = 1600.0 / float(max(w, h))
                    img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
                    w, h = img.size

                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=88, optimize=True, progressive=True)
                img.close()
                img_bytes = buf.getvalue()

            # 計算等比例置中矩形
            ratio = min(cell_w / float(w), cell_h / float(h))
            draw_w = w * ratio
            draw_h = h * ratio
            rx0 = x0 + (cell_w - draw_w) / 2.0
            ry0 = y0 + (cell_h - draw_h) / 2.0
            rect = fitz.Rect(rx0, ry0, rx0 + draw_w, ry0 + draw_h)
            current_page.insert_image(rect, stream=img_bytes)

        doc.save(output_path, garbage=4, deflate=True)
    finally:
        doc.close()


# ======================== API 端點 ========================
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
    # PDF 極限壓縮參數
    compress_preset: Optional[str] = Form("auto"),
    target_mb: Optional[float] = Form(4.5),
    dpi: Optional[int] = Form(75),
    quality: Optional[int] = Form(20),
    keep_color: Optional[bool] = Form(True),
    # 照片批次壓縮 & HEIC 轉檔參數
    max_dimension: Optional[int] = Form(1024),
    out_format: Optional[str] = Form("JPEG"),
    heic_quality: Optional[int] = Form(92),
    # 旋轉刪頁整理 / 安全加密 / 照片排 A4 參數
    page_ops: Optional[str] = Form("[]"),
    security_action: Optional[str] = Form("encrypt"),
    pdf_password: Optional[str] = Form(""),
    a4_layout: Optional[str] = Form("2_up"),
    a4_orientation: Optional[str] = Form("portrait"),
):
    """核心轉檔與壓縮端點"""
    background_tasks.add_task(clean_expired_tasks, BASE_UPLOAD_DIR)

    is_image_batch = mode in ("compress_images", "heic_to_jpg", "images_to_a4_pdf")
    if is_image_batch and len(files) > MAX_IMAGE_BATCH_COUNT:
        raise HTTPException(
            status_code=400,
            detail=f"單次最多僅支援上傳 {MAX_IMAGE_BATCH_COUNT} 張照片，請分批處理",
        )

    task_id = uuid.uuid4().hex
    task_dir = os.path.join(BASE_UPLOAD_DIR, task_id)
    input_dir = os.path.join(task_dir, "input")
    output_dir = os.path.join(task_dir, "output")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    saved_files = []
    total_bytes = 0
    for f in files:
        safe_name = sanitize_filename(f.filename)
        dest_path = os.path.join(input_dir, safe_name)
        with open(dest_path, "wb") as buf:
            shutil.copyfileobj(f.file, buf)
        total_bytes += os.path.getsize(dest_path)
        if is_image_batch and total_bytes > MAX_IMAGE_BATCH_BYTES:
            shutil.rmtree(task_dir, ignore_errors=True)
            raise HTTPException(
                status_code=400,
                detail="單次上傳照片總大小不可超過 50 MB，請分批處理",
            )
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

        elif mode == "organize_pdf":
            base = os.path.splitext(os.path.basename(saved_files[0]))[0]
            out_pdf = os.path.join(output_dir, f"{base}_整理完成.pdf")
            organize_pdf_pages(saved_files[0], out_pdf, page_ops)
            output_files.append(out_pdf)

        elif mode == "security_pdf":
            base = os.path.splitext(os.path.basename(saved_files[0]))[0]
            suffix = "已加密" if security_action == "encrypt" else "已解鎖"
            out_pdf = os.path.join(output_dir, f"{base}_{suffix}.pdf")
            protect_or_unlock_pdf(saved_files[0], out_pdf, security_action, pdf_password)
            output_files.append(out_pdf)

        elif mode == "images_to_a4_pdf":
            out_pdf = os.path.join(output_dir, "照片排版A4報告.pdf")
            images_to_a4_pdf(
                saved_files,
                out_pdf,
                layout=a4_layout,
                orientation=a4_orientation,
            )
            output_files.append(out_pdf)

        elif mode == "compress_pdf":
            for f in saved_files:
                base = os.path.splitext(os.path.basename(f))[0]
                out_pdf = os.path.join(output_dir, f"{base}_min.pdf")
                compress_pdf_extreme(
                    f,
                    out_pdf,
                    preset=compress_preset,
                    target_mb=target_mb,
                    manual_dpi=dpi,
                    manual_quality=quality,
                    keep_color=keep_color,
                )
                output_files.append(out_pdf)

        elif mode == "compress_images":
            for f in saved_files:
                out_img = compress_single_image(
                    f,
                    output_dir,
                    max_dimension=max_dimension,
                    quality=quality,
                    out_format=out_format,
                )
                output_files.append(out_img)

        elif mode == "heic_to_jpg":
            for f in saved_files:
                out_jpg = convert_heic_to_jpg(f, output_dir, quality=heic_quality)
                output_files.append(out_jpg)

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

    except HTTPException:
        shutil.rmtree(task_dir, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(task_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))

    if len(output_files) == 1:
        download_name = os.path.basename(output_files[0])
        final_path = output_files[0]
    else:
        zip_path = os.path.join(task_dir, "轉換成果打包.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in output_files:
                z.write(f, arcname=os.path.basename(f))
        download_name = "轉換成果打包.zip"
        final_path = zip_path

    output_bytes = os.path.getsize(final_path) if os.path.exists(final_path) else 0

    return {
        "status": "success",
        "task_id": task_id,
        "filename": download_name,
        "download_url": f"/api/download/{task_id}?filename={download_name}",
        "original_bytes": total_bytes,
        "output_bytes": output_bytes,
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
                media_type="application/octet-stream",
            )
    raise HTTPException(status_code=404, detail="找不到指定下載檔案")


_s = os.path.join(os.path.dirname(__file__), "../static")
if os.path.exists(_s):
    app.mount("/assets", StaticFiles(directory=os.path.join(_s, "assets")), name="assets")

    @app.get("/")
    async def _r():
        return FileResponse(os.path.join(_s, "index.html"))

    @app.get("/{p:path}")
    async def _spa(p: str):
        f = os.path.join(_s, p)
        return FileResponse(f if os.path.isfile(f) else os.path.join(_s, "index.html"))