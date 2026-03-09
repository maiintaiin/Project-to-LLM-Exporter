# Project to LLM Exporter 🚀

這是一個輕量級的 Python 工具，可以幫你一鍵將整個程式碼專案資料夾打包、匯出成單一的 Markdown 檔案。
非常適合用來把專案餵給 ChatGPT、Gemini、Claude 等 AI 模型，讓 AI 快速了解你的專案架構並協助除錯或開發！

## ✨ 功能特色
* **圖形化介面**：執行後會彈出資料夾選擇視窗，不用在終端機輸入路徑。
* **智慧過濾**：內建完整的黑名單，自動忽略 `.git`、`__pycache__`、`node_modules` 等編譯檔，以及圖片、影片、資料庫 (`.db`, `.csv`) 等非純文字檔，節省 AI 的 Token 消耗。
* **自動命名**：匯出的 Markdown 檔案會自動加上目標資料夾的名稱，方便管理。
* **結構清晰**：在 Markdown 開頭會自動生成專案的樹狀目錄 (Directory Structure)，接著依序印出檔案相對路徑與程式碼內容。

## 🛠️ 如何使用
1. 確保你的電腦有安裝 Python。
2. 下載 `export_to_llm.py`。
3. 點擊兩下執行，或是打開終端機輸入：
    python export_to_llm.py
4. 選擇要整合輸出的資料夾