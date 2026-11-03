import os
import re
import shutil
import time

def sanitize_filename(filename: str) -> str:
    """清理檔名，防止路徑穿越與特殊字元異常"""
    safe_pattern = r'[^\w\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\s\.\-_\(\)\[\]~!@#$%^&+=,;]'
    safe_name = re.sub(safe_pattern, '', filename).strip()
    return safe_name if safe_name else "unnamed_file"

def clean_expired_tasks(base_dir: str, max_age_seconds: int = 1800):
    """清理超過 30 分鐘的過期暫存目錄"""
    now = time.time()
    if not os.path.exists(base_dir):
        return
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            if now - os.path.getmtime(item_path) > max_age_seconds:
                shutil.rmtree(item_path, ignore_errors=True)
