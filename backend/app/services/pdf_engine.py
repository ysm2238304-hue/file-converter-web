import os
import gc
import fitz  # PyMuPDF
from PIL import Image
from app.utils.security import sanitize_filename

def get_pdf_page_count(pdf_path: str) -> dict:
    """取得 PDF 總頁數及是否加密"""
    try:
        with fitz.open(pdf_path) as doc:
            if doc.is_encrypted:
                return {"pages": 0, "encrypted": True, "error": "檔案受密碼保護"}
            return {"pages": len(doc), "encrypted": False, "error": None}
    except Exception as e:
        return {"pages": 0, "encrypted": False, "error": str(e)}

def parse_page_ranges(range_str: str, max_pages: int) -> list:
    """解析自訂頁碼範圍 (例如: 1-3, 5, 8-10)"""
    pages = []
    tokens = [t.strip() for t in range_str.split(',') if t.strip()]
    for token in tokens:
        if '-' in token:
            parts = token.split('-')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                start, end = int(parts[0]), int(parts[1])
                if start > end:
                    start, end = end, start
                for p in range(start, end + 1):
                    if 1 <= p <= max_pages:
                        pages.append(p - 1)
        elif token.isdigit():
            p = int(token)
            if 1 <= p <= max_pages:
                pages.append(p - 1)
    return sorted(list(dict.fromkeys(pages)))

def safe_pdf_to_jpg(pdf_path: str, output_folder: str, dpi: int = 150) -> list:
    """PDF 轉高清 JPG 圖片"""
    os.makedirs(output_folder, exist_ok=True)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    safe_name = sanitize_filename(pdf_name)
    generated_files = []

    try:
        with fitz.open(pdf_path) as doc:
            if doc.is_encrypted:
                raise ValueError("無法轉換加密的 PDF")

            total_pages = len(doc)
            for page_num in range(total_pages):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
                
                jpg_name = f"{safe_name}.jpg" if total_pages == 1 else f"{safe_name}_page_{page_num + 1}.jpg"
                jpg_path = os.path.join(output_folder, jpg_name)
                
                pix.save(jpg_path)
                del pix
                generated_files.append(jpg_path)

                if hasattr(fitz, 'TOOLS') and hasattr(fitz.TOOLS, 'store_shrink'):
                    fitz.TOOLS.store_shrink(100)
                if (page_num + 1) % 10 == 0:
                    gc.collect()
    finally:
        gc.collect()

    return generated_files

def safe_jpg_to_pdf(image_paths: list, output_pdf: str) -> bool:
    """多張 JPG/PNG 圖片串流合併為 PDF"""
    if not image_paths:
        return False
    doc = fitz.open()
    try:
        for img_path in image_paths:
            img_doc = fitz.open(img_path)
            pdf_bytes = img_doc.convert_to_pdf()
            img_doc.close()

            img_pdf = fitz.open("pdf", pdf_bytes)
            doc.insert_pdf(img_pdf)
            img_pdf.close()

        if len(doc) > 0:
            doc.save(output_pdf, deflate=True)
            return True
        return False
    finally:
        doc.close()
        gc.collect()

def merge_pdfs(pdf_paths: list, output_pdf: str) -> int:
    """按傳入清單順序合併多個 PDF"""
    merged_doc = fitz.open()
    success_cnt = 0
    try:
        for f in pdf_paths:
            with fitz.open(f) as sub_doc:
                if not sub_doc.is_encrypted:
                    merged_doc.insert_pdf(sub_doc)
                    success_cnt += 1
        if success_cnt > 0:
            merged_doc.save(output_pdf, deflate=True)
        return success_cnt
    finally:
        merged_doc.close()
        gc.collect()

def split_pdf(pdf_path: str, output_folder: str, mode: str, ranges_str: str = "", chunk_size: int = 1) -> list:
    """PDF 多模式拆分：單頁、自訂區間、定額分卷"""
    os.makedirs(output_folder, exist_ok=True)
    safe_name = sanitize_filename(os.path.splitext(os.path.basename(pdf_path))[0])
    generated_files = []

    with fitz.open(pdf_path) as doc:
        if doc.is_encrypted:
            raise ValueError("加密 PDF 無法拆分")

        total_pages = len(doc)

        if mode == "all_single":
            for p in range(total_pages):
                single_doc = fitz.open()
                single_doc.insert_pdf(doc, from_page=p, to_page=p)
                out_path = os.path.join(output_folder, f"{safe_name}_第{p + 1}頁.pdf")
                single_doc.save(out_path, deflate=True)
                single_doc.close()
                generated_files.append(out_path)

        elif mode == "ranges":
            selected_pages = parse_page_ranges(ranges_str, total_pages)
            if not selected_pages:
                raise ValueError("指定的頁碼範圍無效")
            split_doc = fitz.open()
            for p in selected_pages:
                split_doc.insert_pdf(doc, from_page=p, to_page=p)
            out_path = os.path.join(output_folder, f"{safe_name}_提取頁.pdf")
            split_doc.save(out_path, deflate=True)
            split_doc.close()
            generated_files.append(out_path)

        elif mode == "fixed_count":
            part_idx = 1
            for start_p in range(0, total_pages, chunk_size):
                end_p = min(start_p + chunk_size - 1, total_pages - 1)
                chunk_doc = fitz.open()
                chunk_doc.insert_pdf(doc, from_page=start_p, to_page=end_p)
                out_path = os.path.join(output_folder, f"{safe_name}_Part{part_idx}_第{start_p + 1}-{end_p + 1}頁.pdf")
                chunk_doc.save(out_path, deflate=True)
                chunk_doc.close()
                generated_files.append(out_path)
                part_idx += 1

    gc.collect()
    return generated_files
