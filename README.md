# sansheng-distill · 書籍、影片與人物資料深度蒸餾引擎（繁體台灣在地化增強版）

> 將一本書或一組影片淬煉成可互動瀏覽的單檔案知識地圖；亦可將歷史人物生平整理為可追溯的證據資料庫。

本倉庫為基於官方 [sanshengai/sansheng-distill](https://github.com/sanshengai/sansheng-distill)（v0.11.0）的增強維護版本，核心特色為**全面繁體中文台灣語境支援**與**產物自動台灣化後處理**。

---

## 🌟 本版本特色（Fork Highlights）

1. **繁簡雙相容章節解析**：
   - 增強 `convert_book.py` 之章節正則識別（`CH_PAT`），完整支援台灣繁體出版品（如「第N講」、「第N輯」、全形標點及裝飾符號），避免繁體電子書章節召回率為 0 的問題。
2. **全自動繁體台灣化後處理（Step7 Auto-Localization）**：
   - 生成單檔案 HTML 時，自動調用繁化姬（`zhconvert`）API 進行全頁深度台灣化轉換。
   - 自動將 `<html lang="zh">` 校正為 `<html lang="zh-Hant-TW">`，確保標籤、按鈕、心智圖、正文及自檢清單 100% 符合台灣繁體語境習慣。
3. **無痛追蹤上游更新**：
   - 核心代碼與官方管線高度解耦，未來官方發布新版本時可快速同步合併，兼顧穩定性與最新功能。

---

## 📖 這是什麼

給它一本電子書（`.epub` / `.pdf` / `.txt` / `.azw3` / `.mobi`）或一組影片，跑完標準管線後，產出**一個可以直接在瀏覽器開啟的單檔案互動 HTML 頁面**（`file://` 直開，無伺服器依賴、零外鏈）。

### 五層閱讀漏斗設計：

| 區塊 | 內容特色 |
|---|---|
| **① 全書速覽** | 真封面 + 一句話「餐巾紙公式」 + 核心主張 + 互動式 SVG 心智圖 + 關鍵金句 |
| **② 逐章精讀** | 每章 800–1500 字詳實轉述（手風琴多開，非標籤式粗略提煉） |
| **③ 核心一擊** | 將全書最反直覺的核心論點獨立製作為視覺化模組 |
| **④ 行動 & 自檢** | 因果鏈、心智模型、情境決策規則，搭配第二人稱自檢問答 |
| **⑤ 批判與延伸** | 內在張力、批判四區、正反書評、同類書與作者檔案（均附來源連結） |

---

## 🛠️ 支援的蒸餾模式

1. **單書主管線（Step0-B）**：標準書籍全文深度蒸餾。
2. **影片系列管線（Step0-V）**：多集影片轉寫語料組裝與綜合蒸餾。
3. **創作者思想體系（`creator_corpus`）**：跨媒介歸併單一人物（如創作者、學者）之全部觀點族與思想演變。
4. **證據型人物傳記（`biography_corpus`）**：匯合多來源史實、觀察、裁決與外部核驗，建立人物傳記證據庫。
5. **作者/主題聚合頁（StepA / StepB）**：同一作者 $\ge 2$ 本或同一主題 $\ge 3$ 本時自動生成跨書演變與立場光譜聚合頁。

---

## 📦 安裝與配置

### 1. 安裝為 Agent Skill

**在 Antigravity / Claude Code / Gemini CLI 環境中：**

將本倉庫 Clone 至您的 Skills 目錄下：

**Windows (PowerShell):**
```powershell
git clone https://github.com/lexchang53/sansheng-distill.git "$HOME\.gemini\config\skills\sansheng-distill"
# 若使用 Claude Code:
# git clone https://github.com/lexchang53/sansheng-distill.git "$HOME\.claude\skills\sansheng-distill"
```

**macOS / Linux:**
```bash
git clone https://github.com/lexchang53/sansheng-distill.git ~/.gemini/config/skills/sansheng-distill
# 若使用 Claude Code:
# git clone https://github.com/lexchang53/sansheng-distill.git ~/.claude/skills/sansheng-distill
```

### 2. 安裝 Python 依賴

需要 Python $\ge 3.10$：

```bash
pip install ebooklib beautifulsoup4 pymupdf pillow playwright requests
playwright install chromium

# 處理 .azw3 / .mobi 需要安裝 Calibre (ebook-convert)
# 執行傳記 biography_corpus 路徑需要：pip install "jsonschema>=4"
```

### 3. 環境變數設定

複製設定檔範本：
```bash
cp .env.example .env
```
在 `.env` 中指定資料存放根目錄：
```env
DISTILL_DATA_DIR=./distill-data
```

---

## 🚀 快速使用

安裝完成後，直接在 AI Agent 對話中下達指令：

- *「幫我蒸餾這本書：path/to/book.epub」*
- *「拆解這份 PDF 並製作單檔案蒸餾 HTML」*
- *「建立這個影片系列的思想蒸餾地圖」*

管線執行完成後，系統會自動產出符合台灣用語習慣的單檔案 HTML 頁面。

---

## 🔄 版本更新

要同步上游官方與本倉庫的最新修正，只需在技能目錄下執行：

```bash
git pull origin main
```

---

## 📜 致謝與開源授權

- 原創核心引擎：感謝 [叁笙 (sanshengai)](https://github.com/sanshengai/sansheng-distill) 開發之原創蒸餾管線。
- 繁體化與台灣語境轉換支援：由 [繁化姬 (zhconvert.org)](https://zhconvert.org/) API 提供高精度在地化詞彙轉換。
- 本專案採用 [MIT License](LICENSE) 開源授權。
