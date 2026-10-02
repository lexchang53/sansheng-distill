---
name: sansheng-distill
description: Use when 用户要把一本书全文、单个视频（按 1 集）、YouTube/B站视频系列、一个创作者的全部作品，或历史人物的生平材料做成可追溯的深度蒸馏资料；触发词：蒸馏这本书、拆书、蒸馏视频、视频系列蒸馏、蒸馏 UP 主、人物思想蒸馏、人物传记证据库、历史人物事实核验、传记事实入库。也用于已蒸书库的类别总览、书目与主题聚合。只要字幕摘要、单篇文章写作时不用此 Skill；制作「一页」产品或网站时，本 Skill 只负责公共资料与证据契约，产品规则交给 sansheng-yiye、页面工程与发布交给 sandy-website。
---

# sansheng-distill -- 书籍/视频蒸馏引擎(v3 浏览型)

输入一本书的电子全文或一组视频，先按下文选择路线，再产出一个可本地直开的**单文件交互 HTML 蒸馏页**。Step0–Step7（Step2 分两遍）是导读/视频主管线；完整读者版与严格深读分别使用其专门流程。

**v3 页型 = 浏览型「凝练地图 + 详实正文 + 批判证据 + 页内二级视图」**,5 个 tab 按读者逻辑链组织(① 全书速览 → ② 逐章精读 → ③ 批判与评价 → ④ 行动清单 → ⑤ 延伸阅读);交互层:脑图可点跳章节、章节手风琴多开(目录态默认收起)、两张页内全屏子视图(hash 路由开合)、多主题换肤。每 tab 具体装什么、字段与心理学科学证据层的槽位规格,详见 `references/html-spec.md` §1/§1.1(权威契约,T5 骨架逐字对齐)。

**这是入口编排文件。** 先读本文对齐管线,再在每一步按下表**读对应 reference / 跑对应 script**;references 是各步的执行细则,不要凭记忆做。

**独立书籍路线（先定档，再加载对应流程）**：先按 [high-retention-books.md](references/high-retention-books.md) §0 选择档位；用户明确批准效率与审计粒度取舍时进入 [完整读者版](references/reader-edition-books.md)，不同时加载严格深读的生产与签署流程。**严格深读档**按该文 §0.3 执行来源放行、知识分母、正文、事实/覆盖审阅和数据签署；**导读档**走下表 Step0–Step7。档位只改变生产与证据粒度，来源忠实、真实科学裁决及页面/发布验收仍按实际契约。多书共享车道时再读 [book-batch-operations.md](references/book-batch-operations.md)。已有正式书先用 [redistillation.md](references/redistillation.md) 做整包迁移；项目工具只能证明其实际检查的档位与范围，不把严格工具绿灯或 JSON 齐备当成读者版、科学正确或已上线。

**执行时只选一条生产/审阅路线**：定档后记录本轮终点和当前阶段，按该路线读取细则；已完成的同版本阶段直接复用。读者档的联合审核与停止条件见 reader-edition-books.md §2（开写前的章界预检见 §2.5，审阅改动的应用前检查与审阅—稿子绑定见 §2.6），批次计时与瓶颈处理见 book-batch-operations.md §5。下文主管线的两遍起稿及严格档逐项签署不自动追加到读者档；来源、科学证据及消费者契约仍按实际适用范围执行。

**批量提效的显式可选档**：用户要求逐环节复核成本、减少token/人工耗时并接受低风险质量取舍时，先读 [efficient-book-distillation.md](references/efficient-book-distillation.md)。该档明确来源忠实性、外部事实核查与时间敏感更新的区别，允许在授权范围内取消管理书常规外查、减少低风险重复审阅；仅仍有分母的管理类既有流水线采用该档的项抽样；reader按读者路线生产和抽样，只借用成本/外查政策。默认严格档仍保留。联合检查/局部模型编辑等未验证替代须先试点，不用新指令伪造旧工具所需回执；企业、科学、传记及高后果核验不因管理书提效而降级。

## 先分流：蒸馏对象 → 路径

| 蒸馏对象 | 走路径 |
|---|---|
| 一本书全文 | 先按 high-retention-books.md §0 定档；完整读者版走 reader-edition-books.md，严格深读档走该文 §0.3，导读档走主管线 Step0-B（下表） |
| 单个视频（按 1 集）/ 一个视频系列 | 主管线 Step0-V（下表） |
| **一个博主/人物的全部作品（跨媒介思想蒸馏）** | **StepC · creator_corpus 路径（`references/creator-craft.md`）** |
| **一个历史人物的生平、作品、关系、争议与引语（证据型传记）** | **Biography · biography_corpus 路径（`references/biography-craft.md`）** |

判断口诀：分析单位是「作品」→ 主管线；分析单位是「一个创作者自己的思想输出」→ StepC；分析单位是「一个人的历史生平及其证据」→ `biography_corpus`。StepA/StepB 是主管线的可选聚合步，与后两条人物路径不冲突。

> **企业边界**：企业档案、经营机制、财务及控制权研究由企业研究能力主导；本 Skill 可承接其书籍蒸馏子任务。下述人物标准不放宽企业、科学或高后果书的专门核验。

> **人物路径边界**：`creator_corpus` 归并一个创作者跨媒介表达出的观点族，回答「他的思想体系是什么、如何变化」；`biography_corpus` 汇合多来源的史实观察、分歧与外部核验，回答「发生过什么、证据在哪里、哪些仍有争议」。把传记做成「一页」产品、网站页面、SEO 或正式部署属于下游产品与工程，不在本 Skill 内实现。

> 🪶 **用轻量模型 / 弱 agent 跑本 skill(如 Gemini Flash 级、Antigravity 客户端)→ 先读 `references/flash-mode.md`。**
> 先定档，再读执行卡；卡片的两遍生产判据仅用于导读/视频主管线，不能覆盖读者版或严格深读流程。各档都保留来源与实际验证底线。
> 模型能力不决定质量档位。导读/视频用主管线，读者版与严格深读按各自路线；高能力模型不必额外加载轻量执行卡。

## 路径与变量约定(全文只定义一次)

| 占位符 | 展开为 |
|---|---|
| `$SKILL` | 本 skill 目录(安装后为 `~/.claude/skills/sansheng-distill`) |
| `$DATA` | 书数据根目录,由环境变量 `DISTILL_DATA_DIR` 指定(默认 `./distill-data`) |
| `{slug}` | 书的 ASCII kebab 短名(如 `jinqian-xinlixue`);全站唯一,别撞投资 `NN`/育儿 `pNN` |
| `{书目录}` | 本书数据目录,**纯 `{slug}`**(如 `jinqian-xinlixue`);不含书名,避免中文目录名、git/Windows 友好 |

命令里的占位符替成实值再执行。单书目录首次运行 Step0 时自动建。

## 数据目录约定(单书产物布局)

```
$DATA/
  knowledge-index.json          # 跨书概念索引(全库共享,Step4 维护,自动 .bak)
  {书目录}/
    book.txt                    # 全文(书=Step0-B;视频=Step0-V 组装的转写语料)  -- gitignore
    diagnose.json               # 入书诊断(书=Step0-B;视频=Step0-V 的 video_series 变体)
    raw/                        # 仅视频:各集原始转写 srt/txt(Step0-V)             -- gitignore
    series-input.json           # 仅视频:手写 manifest(Step0-V 输入)
    series.json                 # 仅视频:规范化 manifest(Step0-V 产物,下游只读它)
    comments.json               # 仅视频:观众评论(Step0-V,供 Step3 enrich.reviews)
    distill.json                # 蒸馏主对象 v2(Step2 两遍产:Pass1 骨架 + Pass2 narrative/excerpts)
    _pass2_g*.json              # Pass2 分块中间态(长书按章 fan-out 各组产物,合并回 distill) -- gitignore
    enrich.json                 # 联网增补 v2.1(五个基础键;心理学书加 evidence_page 科学证据层)
    claim-coverage.json         # 仅心理学:Pass1 待审计项到最终 claim 的裁决表
    source-audit.json           # 仅心理学:原文分段、逐项来源记录与四输入 hash
    index-merge.json            # 5-tag 合并清单(Step4 中间产物)
    {slug}.html                 # 单文件交互蒸馏页(Step6 产物,最终交付,≤3MB;真封面 base64 内联,无独立 cover 文件)
    _verify.png                 # Step7 验证全页截图                                  -- gitignore
```

> gitignore(建议在数据目录加 `.gitignore`):`book.txt` / `raw/` / `_verify.png` / `_pass2_*.json` / `*.bak` 不入库(版权原文 / 临时产物);其余(distill / enrich / HTML / index-merge / series / comments / diagnose;心理学另含 claim-coverage / source-audit)可入库。

---

## 导读/视频主管线 Step0–Step7（一览）

每一步的做什么 / 读哪个 reference / 跑哪条命令 / 产物 / 失败降级，完整表在 [pipeline-steps.md](references/pipeline-steps.md)；逐步照做，上一步产物是下一步输入，不凭记忆。

| 步 | 做什么 | 完成判据 |
|---|---|---|
| Step0-B | 电子书 → `book.txt` + `diagnose.json` | exit 0；**exit 3 暂停该来源**（硬门禁①） |
| Step0-V | 视频系列入库：取干净转写、组装语料、抓评论 | `series.json` 生成；build exit 3 同上 |
| Step1 | 书型 + 领域判定（心理学另写 `domain_profile`） | 写入 `distill.json` |
| Step2 | Pass1 凝练骨架 →（可选深读重述层）→ Pass2 详实转述 | 按 `method.md §7` 自查；narrative/excerpts 回填 |
| Step3 | 联网增补；心理学书另产 `evidence_page` + 审计账本 | 五键或第六键齐全；证据不足显式标低置信 |
| Step4 | 跨书索引登记 + 互链（`update_index.py register`，先 `--dry-run`） | register exit 0；禁用 `--force` 绕 exit 1 |
| Step5 | 设计两遍工作法（token plan + signature） | 过反 slop 自审 |
| Step6 | 复制 page-skeleton 填槽，生成单文件 HTML（≤3MB） | 保留完整骨架与交互，不另起极简壳 |
| Step7 | `verify_page.py` 出厂验证 v2 | **exit 0 才算完成**（硬门禁③） |

跑判成败的脚本别用 `| tail` / `| head` 取摘要（管道退出码取最后一段，会吞失败），看完整结尾行或补 `; echo "退出码=$?"`。视频路径 v2 尚未跑过 E2E，遇到骨架/门禁与视频不吻合的坑先记录再修。

### 旧书重蒸分流

已有正式书要替换时，在定档后先读 [redistillation.md](references/redistillation.md)：声明整包角色依赖，使用 `update_index.py replace-book` 撤销取消的旧贡献，心理学补版本绑定的科学终审收据。`register --force` 保留历史增量语义，不能代替整书替换；最终仍须实际页面与项目消费者验收。

## 聚合步骤（可选，不重蒸）

- **StepA 作者演变**：同一作者已蒸 ≥2 部时，只读各书 `distill.json` 聚合成 `author.json` + `author.html`；<2 部不生成。
- **StepB 主题聚合**：同主题已蒸 ≥3 本时聚合成 `topic.json` + `topic.html`（分类地图 / 分歧矩阵 / 维度对照 / 书目导航）；<3 本不生成，成员由 manual 显式圈定。
- 命令、产物、出厂验证见 [aggregation-steps.md](references/aggregation-steps.md)，契约见 `author-craft.md` / `topic-craft.md`。

## 类别框架入口（按需，先于问题专题导航）

用户要理解心理学、管理学等类别全貌，或建立“总—分”书目入口时，读 [category-framework.md](references/category-framework.md)。类别总览、具体问题专题与单书是不同层级；不把某一批书或StepB的分类地图冒充完整学科。类别导航可标空白，不受StepB三成员门槛约束；进入书间争议聚合时仍按StepB契约。单书蒸馏不自动追加类别建设。

## StepC · 人物/博主蒸馏(creator_corpus 路径)

蒸馏对象是「**一个人**的跨媒介全部作品」(视频博主的全部视频 + 专栏/Newsletter + 书 + 播客)时走本路径,**不走 Step0-Step7 主管线** -- 主管线的分析单位是「一部作品」,本路径的分析单位是「人」,基本单元是跨媒介归并后的「观点族」。

- **做什么**:全量采集 → 来源卡建库 → 去重聚类(观点族/主题/关系/时间线) → 总体蒸馏(系统/模型/张力/谱系) → **外部交叉核验 + 通俗化两道闸(必做)** → 产出与网站 creator-distill 契约一致的 10 份数据 JSON + 作者简介。
- **读哪个 reference**:`creator-craft.md`(§0 路由 / §1 总原则「输入全量采集、分析完整建库、展示去重重构」/ §3 P0-P9 阶段管线与批次门 / §5 密度下限 / §6 外部交叉核验 / §7 通俗化两道闸 / §8 展示层信息架构 / §9 数据流规则)。
- **产物**:`{人物项目目录}` 五层数据(L0-L4) + 下游网站数据包；页面渲染、契约测试与部署由消费该数据包的产品工程负责。
- **先例与模板**:`references/creator-craft.md` 记录了经多人物实测收敛的来源卡、证据索引与导出契约；公开测试使用合成 fixture，不依赖任何私有项目目录。
- **与 StepA 的区别**:StepA 聚合「同一作者已蒸的 ≥2 本书」(只读 distill.json,绝不重蒸);StepC 从零蒸「一个人的全部语料」。人物出了书且书已单蒸,两者可共存。

## Biography · 证据型人物传记(biography_corpus 候选路径)

当目标是复原人物生平，而不是总结其自有作品中的思想时，使用 `biography_corpus`。这条路径不生成书籍蒸馏 HTML，也不复用 StepC 的观点族 schema。

- **做什么**：按书章读取与提取完整故事 → 跨书归并、逐章推进全传并复核 → 成批入库与生成投影 → 适用审计及下游交付。正式数据仍按 Source Unit → Observation → signed admission / resolution → Canonical → Editorial 关联；这是数据依赖链，不要求先审完整个资料库才写正文。
- **质量尺度**：普通人物生平默认据成熟书籍高保留重述，尽量保留每本书 70%–80% 的故事与实质信息；跨书合并不丢独有细节，重大冲突才定向加查，不默认追原件或先完成逐段考证。生产与保留口径统一见 `biography-craft.md` §0。
- **读哪个 reference**：`biography-craft.md`。当前实验契约为 `0.9.0-candidate`，机器形状以 `biography-contract-v0.9.0.schema.json` 为准，跨文件闭包以 `scripts/biography_contract.py` 为唯一实现。仓库 SemVer 与数据契约版本是两个独立版本域；候选契约在稳定前可能调整。
- **模型边界**：GLM-5.3 或其他外部模型可以并行做查漏、冲突扫描和修订建议，但只能写 `recommendation_only`；正式事实裁决只允许 manifest 中登记的 `human` 或 `main_agent` reviewer 签署。
- **跨人物隔离**：每个人物都有独立 slug、稳定 subject ID、ID namespace、路由、资源目录和 CSS scope；共享资源必须显式登记为只读并绑定摘要，禁止从另一个人物项目继承隐式默认值。
- **与「一页」产品的边界**：本路径交付公共数据契约、初始化骨架与门禁，不规定某个站点的信息架构、视觉、SEO 或发布流程。下游只读 Canonical / Editorial 投影，不能把页面状态反写事实层。

---



## 硬门禁、铁律与批量规则（停止条件一览）

完整文本在 [pipeline-rules.md](references/pipeline-rules.md)。适用于导读/视频主管线；读者版、严格深读、StepA/B、creator_corpus、biography_corpus 按各自路线契约，不跨档叠加。

1. **硬门禁① 来源**：Step0 或 `build_series.py` exit 3 → 暂停该来源的正文生产，先核原件 / 换本 / OCR；`toc_detected: false` 或 `chapters_detected: 1` 也要停；套装 epub 用 `--volume`；不硬读、不编内容。
2. **硬门禁② 正文质量**：Pass1/Pass2 后按 `method.md §7` 的 G1–G23 自查；命中问题定点回补，不默认整书重蒸。
3. **硬门禁③ 出厂验证**：`verify_page.py` exit 0 才算完成；已知心理学项目必须 `--require-domain psychology --distill … --source …`；绝不放宽阈值或删检查项假过关。
4. **硬门禁④ 批量上站**：蒸多本时 `verify_batch.py --slugs <显式名单>` exit 0 才许上站；名单留着而产物不存在 = 线上 404。
5. **铁律**：论断锚定原文；标题是可反驳的判断句；不编造（金句照录 ≤150 字，高后果书回原书抽检数字）；真封面；外部信息带来源 URL；破折号一律 `--`；上站必须有静态入口 + SEO 头。
6. **批量**：先抽样 1 本再铺量；全局在飞 Pass2 subagent ≤6–8；失败先核盘再重派；`_pass2_gN.json` 合并后清理；同作者 enrich 只搜一次；索引串行登记。

## 环境依赖

- Python **>= 3.10**:`pip install ebooklib beautifulsoup4 pymupdf pillow pytest playwright` + `playwright install chromium`(Step7 需 chromium;`pillow` 用于真封面 / 缩略图的压缩与 base64 内联)。`biography_corpus` 候选路径另需 `jsonschema>=4`。
- azw3 / mobi 输入需 calibre 的 `ebook-convert`(`winget install calibre.calibre`);epub/pdf/txt 不需要。
- **视频系列**(取材 cascade 见 `method.md §V.0`):`yt-dlp`(YouTube 抓字幕 + 抓评论;B站评论走公开 API 免依赖)。B站/抖音的转写需一个字幕/ASR 上游工具(如 `video-to-subtitle-summary`,读其 `AI_DOUYIN_API_KEY`);fetch_comments 的 B站评论无需 key。**无字幕 / 需画面语义**走一个 Gemini 视频分析工具,如独立公开 skill [`sansheng-gemini-video`](https://github.com/sanshengai/sansheng-gemini-video)(读 env `GOOGLE_API_KEY`),装上即可;不装不影响书籍蒸馏与有字幕视频。
