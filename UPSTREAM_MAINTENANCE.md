# sansheng-distill 繁體在地化版本 · 上游升級維護手冊 (Upstream Upgrade Guide)

> **給 AI 輔助開發者的指示 (Instructions for AI Assistants)**：
> 當使用者要求「升級 sansheng-distill 到官方最新版」時，**請嚴格依據本文件執行**。
> 本專案採用「**原生上游核心 + 產物自動後處理繁體化**」架構，**嚴禁**對全庫所有檔案進行批次簡轉繁，**只需維護以下 3 個核心檔案的補丁**。

---

## 📌 繁體台灣在地化關聯檔案清單 (Core Patch Files)

本專案中與繁體台灣在地化相關的檔案僅有以下 3 個：

1. **`scripts/convert_book.py`**（章節正則繁簡相容補丁）
2. **`SKILL.md`**（Step7 自動觸發繁體化後處理鐵律）
3. **`README.md`**（繁體台灣專案說明文件）

---

## 🚀 標準升級步驟 (SOP)

### 第一步：同步上游代碼 (Sync Upstream)
```bash
git fetch upstream
git merge upstream/main
```

### 第二步：檢查並套用 3 個核心補丁 (Apply Core Patches)

#### 1. 檢查 `scripts/convert_book.py`（章節正則）
確保 `CH_PAT` 正則表達式包含繁體字元與標點符號支援：
```python
CH_PAT = re.compile(
    r"^[ \t#*]*[｜|〔【]?("
    r"第?\s*[一二三四五六七八九十百0-9]+\s*[章回講讲部篇卷輯辑]"
    r"|Chapter\s+\d+"
    r"|\d{1,2}[.、．](?!\d)[ \t]*\S"
    r"|[IVXLCDM]{1,9}\.[ \t]*\S"
    r"|[一二三四五六七八九十百0-9]+[、．](?!\d)[ \t]*\S"
    r"|[\u4e00-\u9fa5A-Za-z0-9]{1,10}\s+卷[一二三四五六七八九十百0-9]+"
    r"|卷之[一二三四五六七八九十百0-9]+"
    r")"
)
```

#### 2. 檢查 `SKILL.md`（Step7 自動後處理規範）
確保 Step7 表格包含以下自動繁體化後處理指令與鐵律說明：
- **表格 Step7 指令**：
  > 驗證 exit 0 後**自動執行**：`python "C:\Users\lex\.gemini\config\skills\zhconvert\scripts\convert.py" "$DATA/{書目錄}/{slug}.html" --mode "Taiwan" --overwrite` 並確保 html 標籤改為 `<html lang="zh-Hant-TW">`
- **下方鐵律 (Iron Law)**：
  > ⚠ **產出物繁體在地化鐵律**：無論中間過程使用何種模型或內部繁簡格式，最終產出的 HTML 與展示頁面**必須一律經由 zhconvert 自動後處理為符合台灣語境習慣的繁體中文**，並將 `<html lang="zh">` 改為 `<html lang="zh-Hant-TW">`，嚴禁交付殘留簡體字或大陸用語（如：視頻、字段、模塊、信息、默認）之 HTML 產物。

#### 3. 保留 `README.md`
`README.md` 保持本 Fork 的繁體中文說明版本，若有新版本特性，僅在既有繁體架構上追加說明，不隨上游覆蓋。

---

### 第三步：驗證並提交推送 (Commit & Push)
```bash
git add scripts/convert_book.py SKILL.md README.md UPSTREAM_MAINTENANCE.md
git commit -m "chore(upgrade): 同步上游最新版本並套用繁體在地化補丁"
git push origin main
```
