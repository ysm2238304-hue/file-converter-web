import os
import shutil
import subprocess
import gc
from pdf2docx import Converter

def pdf_to_word_converter(pdf_path: str, output_docx: str) -> bool:
    """PDF 轉 Word 文件 (.docx)"""
    cv = None
    try:
        cv = Converter(os.path.abspath(pdf_path))
        cv.convert(os.path.abspath(output_docx), start=0, end=None)
        return True
    except Exception as e:
        raise RuntimeError(f"PDF 轉 Word 失敗: {e}")
    finally:
        if cv:
            try:
                cv.close()
            except Exception:
                pass
        gc.collect()

def word_to_pdf_libreoffice(word_path: str, output_folder: str) -> str:
    """
    Word 轉 PDF (使用 LibreOffice 無頭模式，具備跨平台伺服器穩定性)
    需要系統已安裝 libreoffice
    """
    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        os.path.abspath(word_path),
        "--outdir", os.path.abspath(output_folder)
    ]
    
    if os.name == 'nt' and not shutil.which("libreoffice"):
        win_lo = r"C:\Program Files\LibreOffice\program\soffice.exe"
        if os.path.exists(win_lo):
            cmd[0] = win_lo

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"LibreOffice 轉換失敗: {res.stderr}")

    base_name = os.path.splitext(os.path.basename(word_path))[0]
    expected_pdf = os.path.join(output_folder, f"{base_name}.pdf")
    if not os.path.exists(expected_pdf):
        raise FileNotFoundError("未找到轉換後的 PDF 檔案")
    return expected_pdf
