# deep-distill-tw · 書籍、影片與人物資料深度蒸餾引擎（繁體台灣在地化增強版）

> 將一本書或一組影片淬煉成可互動瀏覽的單檔案知識地圖；亦可將歷史人物生平整理為可追溯的證據資料庫。

本倉庫為基於官方 [sanshengai/sansheng-distill](https://github.com/sanshengai/sansheng-distill)（v0.11.0）的增強維護版本，核心特色為**全面繁體中文台灣語境支援**與**產物自動台灣化後處理**。

---

## 🌟 本版本特色（Fork Highlights）

1. **單一繁體中文檔案交付（Single Traditional Chinese Deliverable）**：
   - **繁體中文檔名**：最終產物自動由原生的英文/拼音 slug 重新命名為書籍的繁體中文主書名（如 `顛峰心智.html`），維持簡潔俐落的檔案管理。
   - **單一檔案閉環**：自動清理生成過程中的手機過渡檔與方案分流檔，確保每一本書籍目錄下**僅交付 1 個自適應單檔案 HTML**，零冗餘、好攜帶。
2. **極致手機閱讀體驗（Mobile-Optimized Responsive Design）**：
   - **因果流程圖（Napkin Sketch）直式單列佈局**：在手機視窗（$\le 640\text{px}$，如 iPhone 16）下，自動切換為專屬「直式單列版」（寬 350px、方框 250×48px、垂直間距 82px、垂直箭頭與靠右引線標籤），徹底擺脫傳統橫向流程圖在手機上擠壓縮小的問題。
   - **手機 17px 正文同級大字號**：透過強制 CSS 樣式突破 SVG 特異度限制，將方框文字鎖定為 **17px**（與「餐巾紙背面」內文完全等大同級），邊線標籤為 **15px 粗體**，確保清晰舒適的閱讀體驗。
   - **電腦版智慧雙行折行**：電腦寬螢幕模式下自動加寬節點間距（`HGAP = 58`），箭頭上方文字 $\ge 4$ 字自動拆為上下雙行，徹底杜絕文字被方框遮擋或穿透。
   - **即時響應式切換**：內建 150ms 防抖動視窗監聽，在電腦與手機之間平滑自適應，一個檔案同時滿足桌面與行動裝置。
3. **全自動繁體台灣化後處理（Step7 Auto-Localization）**：
   - 經由專屬外掛腳本 `postprocess_html.py` 自動調用繁化姬（`zhconvert`）API 進行全頁深度台灣化轉換。
   - 自動將 `<html lang="zh">` 校正為 `<html lang="zh-Hant-TW">`，修正 CSS 偽元素（如 `.formula-read::before` 為 `"怎麼讀:"`）與 JS 動態字串（如 `'已讀 '`）。
   - 全面將簡體字型（`PingFang SC`、`Microsoft YaHei`）替換為台灣系統繁體字型族列（`PingFang TC`、`Microsoft JhengHei`、`Noto Sans TC` 等）。
4. **繁簡雙相容章節解析**：
   - 增強 `convert_book.py` 之章節正則識別（`CH_PAT`），完整支援台灣繁體出版品（如「第N講」、「第N輯」、全形標點及裝飾符號），避免繁體電子書章節召回率為 0 的問題。
5. **無痛追蹤上游更新（Zero Merge Conflicts）**：
   - 採用外掛式後處理管線架構，**完全不改動上游原生模板 `page-skeleton.html`**，未來官方發布新版本時執行 `git merge upstream/main` 零代碼衝突。

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
git clone https://github.com/lexchang53/deep-distill-tw.git "$HOME\.gemini\config\skills\deep-distill-tw"
# 若使用 Claude Code:
# git clone https://github.com/lexchang53/deep-distill-tw.git "$HOME\.claude\skills\deep-distill-tw"
```

**macOS / Linux:**
```bash
git clone https://github.com/lexchang53/deep-distill-tw.git ~/.gemini/config/skills/deep-distill-tw
# 若使用 Claude Code:
# git clone https://github.com/lexchang53/deep-distill-tw.git ~/.claude/skills/deep-distill-tw
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

管線執行完成後，系統會自動產出繁體中文檔名、專為手機最佳化且支援雙模自適應的單檔案 HTML（如 `顛峰心智.html`）。

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
