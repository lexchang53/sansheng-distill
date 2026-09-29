# sansheng-distill · 書籍、影片與人物資料蒸餾引擎

> 把一本書或一組影片熬成可瀏覽的知識地圖，也把一個人的生平材料整理成可追溯的證據庫。

**中文** | [English](./README_EN.md)

<p align="center">
  <img src="assets/demo.gif" alt="用蒸餾 skill 處理尤瓦爾·赫拉利四本書的成品示範" width="100%">
  <br>
  <sub><em>▲ 用它把尤瓦爾·赫拉利的四本書蒸成一個作品集頁:作者思想演變、概念飄移、母題紅線、跨書互鏈(12 秒靜音循環預覽)</em></sub>
</p>

## 這是什麼

丟給它一本書(`.epub` / `.pdf` / `.txt` / `.azw3` / `.mobi`),或一組影片,它跑完一條多步管線,吐出**一個可以直接雙擊打開的單文件 HTML 頁** -- 不聯網、不依賴伺服器,一個文件就是全部。若輸入目標是歷史人物而非單部作品，它會改走 `biography_corpus`，產出來源、觀察、裁決、規範事實、爭議與外部核驗相互反鏈的結構化資料庫。

它不是"摘要"。摘要是把書壓短、讀完就扔;蒸餾是把書**拆成一張知識地圖**:凝練成一句公式、一張可點的心智圖、一章章能單獨展開的精讀、一組讀完回看的自檢問句,再聯網補上作者檔案、正反書評、跨書觀點,並和你蒸過的其他書自動互鏈。**AI 拆書是拿來當地圖,不是替你讀原書** —— 這句話一直掛在頁面底部。

## 先看產出,再決定裝不裝

它不是一個有界面的軟體,沒有"操作截圖"可看 —— 但它的**成果**是可視的。下面是真實產出(用赫拉利四本書蒸的作品集,以及單本《人類簡史》的蒸餾頁):

<table>
<tr>
<td width="50%"><img src="assets/01-at-a-glance.png" width="100%"><br><sub><b>全書速覽 + 餐巾紙公式</b> —— 真封面、一句公式、核心主張、心智圖、關鍵金句,一屏抓住全書骨架。</sub></td>
<td width="50%"><img src="assets/02-mindmap.png" width="100%"><br><sub><b>可點跳心智圖</b> —— 節點可展開,點一下跳到對應章節。</sub></td>
</tr>
<tr>
<td><img src="assets/03-chapter-deep-read.png" width="100%"><br><sub><b>逐章精讀</b> —— 每章單獨展開,忠實轉述。</sub></td>
<td><img src="assets/04-core-idea.png" width="100%"><br><sub><b>核心一擊</b> —— 全書最反直覺的論點做成可視化。</sub></td>
</tr>
<tr>
<td><img src="assets/05-action-checklist.png" width="100%"><br><sub><b>行動清單</b> —— 決策規則、心智模型、行動路線圖。</sub></td>
<td><img src="assets/06-critique.png" width="100%"><br><sub><b>批判與盲點</b> —— 作者盲點、時代局限,附正反書評來源。</sub></td>
</tr>
</table>

## 它到底幫你做什麼 —— 一頁裡的五段閱讀漏斗

一本書蒸完,是一頁從"3 秒速覽"層層展開到"深挖到底"的閱讀漏斗:

| 段 | 你看到什麼 |
|---|---|
| **① 全書速覽** | 真封面 + 一句"餐巾紙公式" + 核心主張 + 可點心智圖 + 關鍵金句 —— 3 秒抓住全書骨架 |
| **② 逐章精讀** | 每章 800-1500 字忠實轉述,可單獨展開,不是標籤式提煉 |
| **③ 核心一擊** | 把全書最反直覺的那個論點,單獨做成一張可視化 |
| **④ 行動 & 自檢** | 因果鏈、心智模型、決策規則,配一組讀完回看的自檢問句(純瀏覽、無打分) |
| **⑤ 該信幾分 / 再往下** | 批判段、內在張力、正反書評、同類書、跨書回聲、作者檔案 —— 全帶可點來源 |

再疊上三個交互層:**可點跳心智圖**(自繪 SVG,無第三方庫) · **7 套主題一鍵切換** · **跨書知識互鏈**(蒸的書越多,網越密)。

蒸一整套書(如赫拉利四本)時,還會額外合成一個**作者作品集頁**:思想演變時間線、概念在不同書裡的飄移、貫穿多書的母題紅線、"該從哪本讀起"的路線 —— 就是頂部示範裡那個頁面。

## 心理學證據與跨書聚合

心理學書可以啟用嚴格域,把「原書怎麼說」和「外部研究怎麼說」拆成兩層:每條主張都有穩定 `claim_id`,頁面並列顯示原書主張、科學證據、適用邊界與風險。`source-audit.json` 再把 `book.txt`、`distill.json`、固定同目錄的 `claim-coverage.json` 與 `enrich.json` 鎖到同一組 SHA-256,逐項紀錄原文行號。嚴格驗收必須顯式帶原文:

```bash
python scripts/verify_page.py path/to/work.html \
  --distill path/to/distill.json --source path/to/book.txt \
  --require-domain psychology
```

這是一組**條件契約**:普通書與舊頁面不啟用時行為不變。機器閘能抓輸入錯配、漏覆蓋和結構假綠,但不能替代對研究語境與關鍵反例的人工覆審。

跨書還有兩條確定性聚合路徑:同一作者 ≥2 部可生成思想演變頁,同一主題 ≥3 本可生成分類、真分歧、平行對照與維度比較頁。顯式成員清單缺一項就拒絕生成,不會靜默縮小集合;自訂書頁地址只接受安全的站內根相對路徑。真分歧與「回答不同問題的互補鏡頭」分別進入分歧卡和 `parallel_comparisons` 平行對照卡,避免把並列觀點包裝成衝突。

## 還能蒸「一個人」,不只是「一部作品」(v0.5.0)

上面說的都是把**一部作品**蒸成一頁。從 v0.5.0 起多了一條路徑:把**一個人的跨媒介全部作品**——幾百支影片 + 專欄 / Newsletter + 書 + 播客——蒸成他的思想全景。

分析單位不同:前者問"這本書講了什麼",後者問"這個人的觀點體系是什麼、這些年怎麼變的"。所以它不是把每部作品各蒸一遍再拼起來,而是全量採集 → 逐條建證據庫 → 跨媒介去重聚類成**觀點族**(同一個觀點他在影片裡說過、在 Newsletter 裡寫過,只算一次) → 再蒸出系統、行動模型、思想軌跡與內在張力,並做一輪中英文第三方解讀的交叉核驗。

首個案例是 Dan Koe:162 支影片 + 212 封 Letters + 25 章書,合成 399 份來源、1,836 條證據、299 個觀點族。

## 還可以建立證據型人物傳記庫

人物的「思想作品庫」和「歷史傳記庫」不是一回事。`creator_corpus` 從一個創作者自己的影片、文章、書和播客中歸併觀點族；新的 `biography_corpus` 則匯合檔案、書信、研究、館藏與可靠網頁，逐條回答：發生過什麼、證據在哪、不同來源為何衝突、哪些結論仍應保留爭議。

這條路徑採用單向證據鏈 `Source Unit -> Observation -> MergeDecision -> Canonical -> Editorial -> Projection`，並提供實驗性 v2 候選 schema、初始化器和三層門禁。當前數據契約版本是 `0.9.0-candidate`；它與倉庫 SemVer 屬於兩個獨立版本域，穩定前仍可能調整。GLM-5.3 等外部模型可以並行查漏或給出修訂建議，但只能留下 `recommendation_only`；正式裁決必須由 manifest 登記的 `human` 或 `main_agent` reviewer 簽署。每個人物的 namespace、路由、資產和 CSS scope 獨立，批次審計會攔截跨人物串線。

```bash
python scripts/biography_store.py init \
  --store-root ./biography-data/sample-scholar \
  --slug sample-scholar --subject-id per-sample-scholar \
  --catalog-name "Sample Scholar" --language en

python scripts/biography_store.py audit \
  --store-root ./biography-data/sample-scholar --mode strict-data
```

完整工作流與產品邊界見 [`references/biography-craft.md`](./references/biography-craft.md)。本倉負責公共資料契約與驗證，不負責某個「一頁」站點的視覺、SEO 或部署；下游產品只能讀取投影，不能反寫事實層。

## 什麼時候用

對 Claude 說 *"蒸餾這本書"* *"拆這本書"* *"distill this book"* *"蒸餾這個影片系列"* *"蒸餾這個部落客"* *"建立人物傳記證據庫"* *"核驗這個歷史人物的生平材料"*,或直接丟一個電子書文件讓它做蒸餾頁 -- Claude 會接起這個 skill,選擇對應管線。

**不適合**:寫文章、剪影片、只想要字幕或一段普通摘要，也不單獨承擔網站頁面工程與發布。

## 安裝

作為 Claude Code plugin(推薦):

```bash
claude plugin marketplace add sanshengai/sansheng-distill
claude plugin install sansheng-distill
```

或手動:clone 後軟鏈進 `~/.claude/skills/`:

```bash
git clone https://github.com/sanshengai/sansheng-distill.git
ln -s "$PWD/sansheng-distill" ~/.claude/skills/sansheng-distill
```

然後重啟 Claude Code。

### 國內加速下載

GitHub 直連不暢時，給 clone 地址前面加一層公共鏡像即可（下載原始碼 zip 同理）：

```bash
# 加速 clone（把 gh-proxy.com 換成 ghfast.top 即備用鏡像）
git clone https://gh-proxy.com/https://github.com/sanshengai/sansheng-distill.git
```

插件市場方式暫無穩定國內鏡像；網路不暢時用上面的加速 clone + 軟鏈。

## 更新

升級到新版，取決於你當初怎麼裝的：

- **插件市場裝的**：`claude plugin marketplace update` 刷新市場，再 `claude plugin update sansheng-distill`
- **clone + 軟鏈裝的**：進本倉目錄 `git pull`（軟鏈即時生效，不必重裝、不必重連）

**怎麼知道有新版**：看本倉 [Releases](../../releases)；點倉庫右上角 **Watch → Custom → Releases**，發新版時 GitHub 會通知你。每版改了什麼見 [CHANGELOG](CHANGELOG.md)。

## 快速上手

```bash
python --version             # 需要 Python >= 3.10
pip install ebooklib beautifulsoup4 pymupdf pillow playwright
playwright install chromium
# 只有 biography_corpus 候選路徑另需：pip install "jsonschema>=4"
# .azw3 / .mobi 輸入還需 calibre 的 `ebook-convert`
cp .env.example .env        # 然後填 DISTILL_DATA_DIR(蒸影片再填影片那幾個 key)
```

然後在 Claude Code 裡讓它蒸一本書即可。八步管線(Step0-Step7)寫在 [`SKILL.md`](./SKILL.md),每步細則在 [`references/`](./references/) 下。

## 配置

- `DISTILL_DATA_DIR` —— 書數據與產物存哪(見 [`.env.example`](./.env.example))。
- 影片路徑(可選):`GOOGLE_API_KEY`、`AI_DOUYIN_API_KEY`、`yt-dlp`。
- 主題:頁面自帶 7 套配色,右下角切換器隨時換。

## 配套文章 · Article

一篇講透"這個 skill 怎麼來的、融合了哪些拆書流派、我們又加了什麼原創"的公眾號文章即將發布,發布後補上連結。

## 關於作者 · About the author

<p align="center">
  <a href="https://sanshengai.top"><strong>🌐 網站 sanshengai.top</strong></a> ·
  <a href="https://namecard.xiaoyuzhoufm.com/nnl8x"><strong>🎧 小宇宙</strong></a> ·
  <a href="https://weibo.com/u/7546221967"><strong>微博</strong></a> ·
  <a href="https://www.xiaohongshu.com/user/profile/5c716b6d000000001000f5c4"><strong>小紅書</strong></a> ·
  <a href="mailto:sandypoli@gmail.com"><strong>✉️ 信箱</strong></a>
</p>

我是**叄笙**,用 AI 做內容、也用 AI 造工具。這個 skill 是我做個人站「[叄笙早安 AI](https://sanshengai.top)」的內容時,在真實工作流裡一點點磨出來、再清洗脫敏開源的。覺得有用,歡迎來[網站](https://sanshengai.top)逛逛,或**掃碼關注公眾號「叄笙早安AI」**(公眾號沒有跳轉連結,掃碼最快):

<p align="center">
  <img src="assets/qrcode-gongzhonghao.png" alt="微信公眾號 叄笙早安AI" width="200">
  <br><sub>微信掃碼關注 · 叄笙早安AI</sub>
</p>

## 致謝與依賴 · Credits & Dependencies

### 致謝(借鑑來源)

這套蒸餾方法不是憑空來的,研習、吸收了社區裡不少優秀的"拆書 / 讀書 / 前端"作品再融合,特此致謝:

- **[crayon-ai/book-to-webpage](https://github.com/crayon-ai/book-to-webpage)**(MIT)—— 頁面設計(布局、配色、主題切換器)的主要參照,借鑑最多。
- **李繼剛** 的書籍蒸餾 skill —— "餐巾紙背面 / 餐巾紙公式"這一思路來自他(僅此一處,非整套方法)。
- Anthropic 的 **frontend-design** 與寶玉的 **baoyu-design** —— 前端審美與設計取向上的影響。

> 心智圖(自繪 SVG)、章節展開、主題切換等交互均為自研實現,本倉**不捆綁任何第三方庫代碼**;上述均為思路借鑑。

### 運行依賴(請自行安裝,未捆綁)

| 依賴 | 用途 | 何時需要 |
|---|---|---|
| `ebooklib` · `beautifulsoup4` · `pymupdf` · `pillow` · `playwright`(+ `playwright install chromium`)| 解書 + 出廠驗證 | 必需 |
| `jsonschema>=4`（MIT） | 人物傳記實驗性 v2 候選 schema 與跨文件審計入口 | 僅 `biography_corpus` 路徑 |
| `calibre`(`ebook-convert`)| 轉 `.azw3` / `.mobi` | 僅這兩種格式輸入時 |
| `yt-dlp` | 抓字幕 / 評論 | 僅影片系列路徑 |
| 一個字幕 / ASR 工具 | 轉寫無字幕影片 | 僅蒸"非 YouTube 且無字幕"的影片系列時 |
| 姊妹 skill [`sansheng-gemini-video`](https://github.com/sanshengai/sansheng-gemini-video) | 看懂影片畫面 / 音訊 | 僅蒸需要視覺理解的影片系列(蒸書不需要) |

**許可說明**:本倉以 MIT 分發,不捆綁第三方代碼。上述運行依賴由你自行安裝,各自保留其許可。

---

**用著順手的話，點個 ⭐ 吧** —— 這是我判斷「要不要繼續做下去」最直接的信號。

## License

[MIT](LICENSE) © 2026 叄笙 (sansheng)
