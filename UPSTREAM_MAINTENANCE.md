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

### 第一步：環境與身份自動判定 (Auto-Detect Role via Git Remote)

執行以下指令檢查目前遠端倉庫：
```bash
git remote -v
```

- **情況 A（維護者模式 · 有 `upstream`）**：
  若存在 `upstream`（指向官方 `sanshengai/sansheng-distill`），代表為倉庫維護者，執行以下指令拉取並合併官方最新代碼：
  ```bash
  git fetch upstream
  git merge upstream/main
  ```
  *(合併完成後，請繼續執行下方的「第二步：檢查並套用 3 個核心補丁」)*

- **情況 B（一般用戶模式 · 僅有 `origin`）**：
  若**無** `upstream` 遠端，代表目前為終端使用者，請直接自本 Fork 倉庫拉取已維護完成的最新繁體版，**不可**執行後續手動補丁步驟：
  ```bash
  git pull origin main
  ```
  *(終端用戶至此更新完畢)*

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

#### 2. 檢查 `SKILL.md` 與 `references/pipeline-*.md`（Step7 自動後處理規範）
確保包含以下自動繁體化後處理指令與鐵律說明：
- **`SKILL.md` description**：包含 `或當使用者要求「更新/升級 sansheng-distill 技能」時...` 觸發指示。
- **`references/pipeline-steps.md` 表格 Step7 指令**：
  > 驗證 exit 0 後**自動執行**：`python "C:\Users\lex\.gemini\config\skills\zhconvert\scripts\convert.py" "$DATA/{書目錄}/{slug}.html" --mode "Taiwan" --overwrite` 並確保 html 標籤改為 `<html lang="zh-Hant-TW">`
- **`references/pipeline-rules.md` 下方鐵律 (Iron Law)**：
  > ⚠ **產出物繁體在地化鐵律**：無論中間過程使用何種模型或內部繁簡格式，最終產出的 HTML 與展示頁面**必須一律經由 zhconvert 自動後處理為符合台灣語境習慣的繁體中文**，並將 `<html lang="zh">` 改為 `<html lang="zh-Hant-TW">`，嚴禁交付殘留簡體字或大陸用語（如：視頻、字段、模塊、信息、默認）之 HTML 產物。

#### 3. 保留 `README.md`
`README.md` 保持本 Fork 的繁體中文說明版本，若有新版本特性，僅在既有繁體架構上追加說明，不隨上游覆蓋。

---

### 第三步：驗證並提交推送 (Commit & Push)
```bash
git add .
git commit -m "chore(upgrade): 同步上游最新版本並套用繁體在地化補丁"
git push origin main
```

### 第四步：自動雲端備份至 P 磁碟 (Auto-Backup to P Drive)
提交並推送到 GitHub 後，**必須自動調用 skills-sync** 進行本機至 P 磁碟的鏡像同步，確保多台電腦無縫銜接：
```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.gemini\config\skills\skills-sync\sync-skills.ps1" -Mode Backup -SkillName "sansheng-distill"
```
*(升級流程至此全流程閉環完畢)*

