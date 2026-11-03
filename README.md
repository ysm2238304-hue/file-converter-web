# DocuMorph Pro - 現代化多功能檔案轉換 Web 平台

由桌面端 PyQt6 專案全面現代化轉移之 Web 專案，採用 FastAPI (後端) + Vue 3 / Vite / Tailwind CSS (前端)。

## 系統特性
- 📑 **PDF 合併/拆分**：自訂範圍、全部分解、定額分卷，支援流暢卡片排序。
- 🖼️ **PDF ↔ JPG/PNG**：採用 PyMuPDF 核心高速光柵化，自動垃圾回收防記憶體洩漏。
- 📝 **PDF 轉 Word**：整合 pdf2docx 高精確度文件結構解析。
- 📄 **Word 轉 PDF**：跨平台使用 LibreOffice Headless 轉換，免 Windows COM 依賴。
- 📦 **自動打包**：多檔案轉換完成後自動封裝為 .zip 供單鍵下載。
- ⏳ **生命週期防禦**：背景定時自動銷毀 30 分鐘前過期暫存檔案。

## 目錄架構
- `backend/`: FastAPI 後端程式碼、Dockerfile、轉檔服務引擎
- `frontend/`: Vue 3 + Vite + Tailwind CSS 前端專案
