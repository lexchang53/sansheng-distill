# biography_corpus -- 证据型人物传记资料库

这条路径用于把一个历史人物的生平材料整理成**可追溯、可争议、可迁移、可发布**的数据资料库。它回答的不是「这个人表达过哪些思想」，而是「发生过什么、依据是什么、不同来源如何冲突、正式版本为何这样裁决」。

> 当前数据契约是实验性的 `0.9.0-candidate`。数据契约版本与本仓库 SemVer 属于两个独立版本域；候选期字段仍可能调整。若宿主直接复用源码 API，应固定到明确的仓库 tag（本次发布为 `v0.8.0`），不要跟随可变的 `main`。

## 0. 路由与边界

| 目标 | 应走路径 |
|---|---|
| 蒸馏一本书或一组视频 | Step0-Step7 主管线 |
| 归并一个创作者自己的跨媒介观点 | `creator_corpus` |
| 汇合多来源，建立人物生平、作品、关系、争议与引语的证据库 | `biography_corpus` |
| 设计页面、SEO、站点路由或执行部署 | 下游产品/网站能力 |

`biography_corpus` 负责公共资料模型、初始化、审计和发布前门禁。它不规定某个网站长什么样，也不把页面交互状态写回事实层。下游只能消费投影。

## 1. 单向证据链

```text
Source Unit -> Observation -> MergeDecision -> Canonical -> Editorial -> Projection
     |                                        ^
     +-> ExternalVerification ----------------+
```

- **Source Unit**：一本书的一版、一篇论文、一件馆藏记录或一个可复查网页，不是笼统的机构名。
- **Observation**：来源在某个明确 locator 上实际支持的最小主张。解释与事实必须分开记录。
- **MergeDecision**：正式 reviewer 对 Observation 的接纳和 Canonical 写入方式作出的签署裁决。
- **Canonical**：跨来源合并后的现役人物事实，分为 People、Events、Works、Relations、Controversies、Quotes 六类。
> 🔴 **抽取阶段的字段上限决定了下游能写多厚**（2026-08-24 立）。
> 提炼提示词 v6 曾规定 `quote_text` ≤ 80 字符并明令「超过就挑一句或直接放弃」、
> `detail_hint` ≤ 120 字符、每包最多 10 条候选。结果是素材在入库时就被切成碎片：
> 爱因斯坦线的旅行日记 21.5 万字，全书只抽出 **1 条**观察；主传写到 4.7 万字，
> 只用掉叙事主干源文的 **5.8%**，读起来像简报。
>
> 写主传的人手里从来没有长文本，**这不是笔力问题，是米不在锅里**。
> 改写作规范、喊「写深一点」都无效——形容词改不动这个。
>
> v7 已取消引文上限、把细节栏改为下限 80 / 上限 400 字符、候选条数按包长给下限。
> 为新人物设计提炼契约时，**先问一句「这个上限会不会让下游没东西可写」**。
>
> 配套：产品层的篇幅与深度判据见 `sansheng-yiye/references/deep-prose.md`
> （现行口径：≥400 字/幕 · ≥70% 源段覆盖 · 40–80% 等密比；一手直引须贴合该幕，
> **不要求每幕一条**）。这些是有对应源段的产品叙事检查，不是全部人物、全部来源
> 的统一成稿字数或引文定额；缺少可核细节时须写明空窗，不能为达比值补造现场。
>
> 一手材料另有一条路：当事人的日记、书信、文集可按「本人文字区间 + 归属分层」
> 直接建**私有定位索引**，不必先把原文压成短候选。爱因斯坦线的
> `工具/extract_first_person.py` 曾定位 2,263 条／21 万字；这个数字表示可回查的
> 私有源段，不是可整段公开引用的许可。公开叙事重组事实、动作与感受，仅在权利允许的
> 范围内用必要短引，标明版本与说话者。先划清编者前言、转引、伪托语录与他人评价的
> 边界——把编者的话当本人原话，读者完全无从察觉。

### 多来源厚传的段落与场景回查

书籍、日记、书信与后人补记一起进入传记时，先按**版本和声音**分别冻结段落分母与
定位摘要。模型可并行提取“值得讲的单元”，但每批保存输入范围、行号和
`recommendation_only`；结果必须验证能解析、定位在所给范围内。用候选行号与冻结段落
求交集，只能找出**可能被漏掉的段落**，不能宣称信息留存率；无交集段要连标题、日期、
上下文人工回看。信头、收信人和签名可作结构段，却须与相邻正文绑定；被引用的他人诗文、
童话或信件留作品关系及阅读情境，不冒充传主亲历或直接重刊。

模型给出的“短锚”常是意译，不能只检查字段非空。若定位依赖原文短锚，输入先固定
版本与段落 ID；回文必须同时给段落 ID 和**在该段逐字连续出现**的短语，由脚本逐条
核对段号、子串、单元 ID 与缺项。失败项退回同一输入包重新回锚；通过只表示候选能
回到所读材料，不表示材料中的主张已被史实核验。若一个包触及候选条数上限，还要人工
复看未命中段和多事件长段，不能把满额回文当成全书覆盖。现代传记把本人事后回忆、
他人编纂、作者想象的动作或心理写成连续场面时，先拆声音与时间层，再决定哪些细节
能进入公开叙事。

每个有价值的源段最终有明确去向：进入某一主场景、作为背景、与另一段合并、暂缓，
或附理由排除；重复使用应标出交叉关系。比较多版回忆和同期记录时，先分别说清
“谁在何时写、写的是何时的事、是亲见还是转述”，再决定能否合成一个镜头。
模型没识别代词所指、把文学化的视觉描写当感官经历、把观点写成已证成效时，
回到整段和邻段修正。场景卡至少承载时间、地点、在场者、动作、转折、后果、
感受的来源和未决冲突，供长篇叙事选择；不要把每张卡压成一句年表。

逐段候选索引还有三个防漏检查：`structure` 只给真正没有生涯信息的标题等，
“困难刚要克服，随后发生一件事”这类承前启后的段落须接到冲突场景；含引文的段落先
分开本人回忆、修辞和他人文字，不能因段尾引文删掉段首经历；一个长段若同时包含
约定、出行、暂别和再次共读等动作，应拆出多个信息单元，不能以一句书名概括。
检验人物代词时连读前后段，明确姓名后再写关系；若模型给出“指代不明”或漏掉
姓名，应回原文核，而非直接让匿名人物进入关系图。以上判断仍留候选身份，直至
主审签署源段去向和对应事实。

### 年谱与长扫描本的防漏复核

年谱、编年附录和长篇扫描本可按页段交给模型提出场景候选，但须另从原书建立
**逐年覆盖表**：列出原书实际出现的年份、对应页段、模型候选数和人工去向；候选为零
的年份也要回看，不能用“模型没有提到”推断那年没有可讲的经历。一个长段含多次
任教、迁居、写作或家庭变化时拆为不同人生单元；几页重复追述同一件事则分别保留
源段，合并到同一人生单元。模型碰到每包输出上限或扫描本的末页时，复查该包首尾
是否截断，并对漏年定点补抽。逐年覆盖只证明这一本书得到处理，不证明全生涯史实
或其他来源已经覆盖。

定位账同时保留 **PDF 页、印本页和 OCR 行号**；三者不得混称。机器可用输入行号
校正模型错报的页码，但这只修复候选锚点。跨页题名、引文和事件须连看相邻书影，
核对说话人、完整句子与时间；涉及人名、作品名、日期、关键动作的 OCR 字也要回到
影像，不能以可检索文字代替原页。模型把原书年谱复述正确仍只有**同一来源**：若
同期报刊、档案或版本版权页给出不同日期，分别记 Observation 与冲突去向，暂停
确定性表述，不能把模型回显或页码校正算成独立佐证。

用户要求高信息保留时，保留的是经去重、核对后可复述的**事实、关系、过程与感受**，
并报告其相对于源段分母和关键转折的覆盖，绝不把 60%–80% 理解为逐字转载比例。
检查最终正文的转场、日常细节与当事人代价，也检查高密素材是否仍只停留在私有索引，
没有进入读者真正能读到的叙事。

同一事件若有本人同期信件、公开演说、同行者记录、馆藏照片和后出研究，逐件保留
**成文日期、说话者、受众、媒介及证据角色**；公开立场与私人感受可以并列，不能
改写成一段全知视角的独白。目录条目只能证明材料存在，不等于已经读过全文；网页转录
与原件影像、录音尚未核异时要标出层级。不同收信人的信即使句子相近，也不能合成
同一封信。照片说明可确定被馆方标注的人物和场合，不能据表情补写想法；图像使用权
单独核定，链接可查阅不等于可嵌入公开页面。

有声档案须分开**当事人发声、翻译／传译者的话、主持人的介绍和馆方后配的转录**；
时间戳与说话人标签先对音轨复核，未听原录音时只按“馆方转录记载”写，不描述音色、
停顿或掌声。连续多年的立场变化也须按日期各立 Observation：早期反对、后期支持、
当事人自述的理由和机构替她归纳的外部动因是四种主张，不能压成“某人说服了她”。
传主的偏见或历史误读同样要保留为**当时的观点**，另用可靠历史研究核事实；
不能因传主在另一领域的贡献而删去，也不能把错误观点放进事实年表。人物的复杂性
来自可证的选择及局限，不靠虚构瑕疵或替她辩护。

来源覆盖、叙事覆盖和读者实际可见的覆盖分别报告。长书的段落分母可先机械冻结，
但模型返回的非空候选、与段落行号相交、`hold` 有记录，均不能冒充已逐段审读或
独立人生单元已进入正文。先用两个不同人生阶段或材料性质的样章验一遍来源、
事实裁决、连续阅读和页面证据入口；若成年阶段仍只能借童年自传，先补同期材料，
再考虑铺写全传。

修补已发布人物时，先读**实际页面的相邻章节**，再回查编辑层与冻结书源。某一幕的
已选源段没讲到核心转折，不等于整本已入库的书没有讲；先在该书目录及全文定位
所需章节，记录“来源已有而抽样漏选”或“来源确缺”，再补 Observation 和裁决。
乔布斯 Apple II 的 1977 年工程与产品化、Pixar 1995 年 IPO 时机，曾因只核所选
段落而被正文误写为“冻结书源未载”。类似问题不能只改公开句子：源段、正式观察、
Canonical、编辑正文和读者页须一起复核。章标题若承诺某一场转折，正文要让读者
看见当时的选择、参与者和后果，不能以多年后的结果倒看代替过程。

Macintosh 接管段也曾有同类误判：场景正文写“书源未给出直接记载”，而已冻结的
艾萨克森传记连续写了拉斯金的低价方案、68000 样机、团队争执和他离场的过程。
修复这种叙事桥时，应把**方案与人的冲突**拆成可读的连续场景，分别记发起者、
工程者、软件贡献者与取得控制权的人；当两份材料把“接管”放在不同月份，保留
各自观察的时间和事件口径，不强压成精确的一天。完稿后反查章标题、相邻章节、
来源定位、正式观察、签署裁决、Canonical、段落风险复核与网站投影，任何一层的
旧说法都不应悄悄留下。

章节数、段落数和字数只用于发现压缩异常，不是合格证明。每章只有三段时尤其要
连读前后章，检查多年经历是否被塞进一段、人物关系是否只在结论中出现。先修
遗漏的过程和因果桥，再考虑补句；新增细节仍逐项受来源、声音和权利边界约束。

- **ExternalVerification**：对既有主张的外部复核。它必须反链来源和目标，但不能越过 Observation / MergeDecision 直接改写 Canonical。
- **Editorial**：章节、概览、布局和档案等叙事选择。它可以选择怎样讲，不能创造新的事实。
- **Projection**：给页面、API 或其他消费者的只读输出。

JSON Schema 只验证单个文档的形状；`scripts/biography_contract.py` 验证跨文件语义闭包。CLI、宿主编译器和测试必须调用这一份实现，不能分别复制一套近似规则。

## 2. 初始化一个独立人物 store

公共入口只有一个：`scripts/biography_store.py`。新人物从 v2 骨架开始，不复制另一个人物的目录。

```bash
python scripts/biography_store.py init \
  --store-root ./biography-data/sample-scholar \
  --slug sample-scholar \
  --subject-id per-sample-scholar \
  --catalog-name "Sample Scholar" \
  --language en
```

`--language` 默认 `zh-CN`。`catalog_name` 只是 draft/bootstrap 阶段的兼容提示；发布前必须与主人物 Canonical Person 的 primary name 一致，人物姓名的正式真源始终是 Canonical Person。

初始化器创建 manifest、六类 Canonical JSONL、治理账本和 Editorial 空骨架。它必须拒绝覆盖已有正式数据；确需迁移时先用 `audit` 盘点，不要重新初始化。

建议布局：

```text
sample-scholar/
  manifest.json
  source-registry.json
  observations.jsonl
  merge-decisions.jsonl
  external-verifications.jsonl
  source-coverage-decisions.jsonl
  work-classifications.jsonl
  work-identity-decisions.jsonl
  quote-attribution-audits.jsonl
  prose-risk-reviews.jsonl
  changesets.jsonl
  model-recommendations.jsonl
  media-assets.jsonl
  canonical/
    people.jsonl
    events.jsonl
    works.jsonl
    relations.jsonl
    controversies.jsonl
    quotes.jsonl
  editorial/
    chapter_order.json
    chapters.json
    overview.json
    layout.json
    dossier.json
    media.json
```

## 3. Manifest v2：身份与目录不可混为一谈

`manifest.json` 使用 `biography-store-manifest-v2`，并显式声明：

- `subject.slug`：目录和路由 namespace；目录名必须与它相等。
- `subject.subject_id`：稳定历史人物 ID；它不必由 slug 推导。
- `subject.id_namespace`：新对象 ID 的 namespace；必须与 slug 相等。
- `canonical` / `editorial`：全部文件映射，消费者不得靠固定文件名猜测。
- `governance`：正式 reviewer allowlist、Source Registry 和所需账本。
- `projection`：人物专属路由、资源路径、CSS scope 与显式共享资源。
- `publication`：draft / review / published 状态及发布所需元数据。

manifest 不复制人物姓名。主人物 Canonical Person 是姓名和 name forms 的唯一真源。旧 ID 若已被外部引用而不能重写，应通过显式 legacy alias 迁移，不要为追求整齐破坏稳定引用。

## 4. 先建来源，再写观察

每个 Source Unit 至少要能回答：

1. 这是哪一个具体版本、见证本、网页快照或馆藏对象？
2. 读者如何回到支持主张的准确位置？
3. 这个来源能证明什么，又不能证明什么？
4. 它与哪些 Observation、ExternalVerification 双向连接？

Locator 应使用来源本身的定位体系：卷、篇、叶、页、行、条目或 accession 各归各位，不能把它们互换。传统文献、手稿和多版本作品应保留 edition / witness；博物馆对象应保留 accession。历法日期也要保留原始书写，不能只留下换算后的 ISO 日期。

Observation 一条只承载一个可审计主张，并显式携带 `subject_id`、`id_namespace`、`source_id`、locator、certainty 与 statement kind。来源正面支持、来源内部解释、编者推断和未知状态不可揉成一句。

Observation 的 statement 只记录该来源及其定位段能支持的内容；“原刊尚未找到”“影像待核”等取证进度写入来源覆盖或审阅记录，不写成来源事实。取得新版本或原页后，回查旧 Observation 与正文里这类临时措辞，保留原来源的说话人，同时更新取证状态和受影响的裁决。

## 5. MergeDecision：两次判断，exact-once

每条 Observation 先经过 `observation_admission`：

- `accept`：允许进入正式事实合并流程。
- `hold`：材料值得保留，但当前不足以裁决。
- `reject`：不进入 Canonical；拒绝原因仍留在账本。

只有 `accept` 才能再有一条 `canonical_resolution`，其 verdict 为 `adopt / create / enrich / correct / merge`。由此形成 exact-once 约束：

- 每条现役 Observation 恰有一条 signed admission。
- accepted Observation 恰有一条 signed resolution；hold/reject 不得有 resolution。
- 每个 active/hold Canonical 都有可追到 Observation 的正式 resolution。
- redirect 只能由 signed merge 产生，并一步指向同类型的最终 active 或 hold 对象；只有 active 目标才能暴露为公开 alias。

`status=superseded` 只保留审计历史，不参与现役 exact-once。迁移旧资料时，无法重建历史创建动作可使用 `adopt + migration_basis`；不知道的历史审核时间写 `null`，不要补造精确时间。

## 6. 六类 Canonical 的历史资料语义

### 6.1 Person 与姓名形式

主人物必须有一个 primary name。字、号、别名、异体、罗马化形式分别进入稳定的 `name_forms`；每个 name form 自带语言、文字体系、证据、适用时期和确定性。姓名形式不是新的 Person，也不要求每个人都具备罗马化形式。

### 6.2 Event 与日期

事件日期可保留原历法、原文、展示标签、精度和起止范围。若提供换算日期，还要记录换算方法、依据 Observation 与换算 certainty。来源只到某年时不得伪造月日。

### 6.3 Work 的三个层级

区分 intellectual work、textual expression 与 material manifestation：作品概念、某个文本版本、某件实物载体不是同一个对象。手稿、刻本、译本或馆藏卷轴必须通过明确关系连接，不能因为标题相同就跨层级 merge。

### 6.4 Relation

active Relation 必须有可解析端点，其中至少一个是主人物。`counterpart_hint` 只能帮助人工处理 hold 数据，不能替代正式端点。

### 6.5 Controversy

争议由一个 question、两个或更多 positions 及各自的 source/evidence 构成；不要预设所有争议都只有两方。consensus 可为 none / partial / majority / resolved / unknown。证据支持多种说法时，应保留结构化分歧，不要把单一猜测写成 confirmed 事件。

### 6.6 Quote

引语必须区分作者、作品、实际说话者和文本形式。persona、narrator 与历史人物本人不是同一语义；原文、异文和翻译进入不同 text form，并分别绑定 witness / locator / evidence。翻译不能冒充原文，伪托语句不能把主人物标为事实 speaker。

### 6.7 Media ledger

媒体不是事实层的装饰字段。资源账本要分别记录 creator、object attribution、depicted subject、真实性判断、权利状态、来源和文件摘要。一个作品是谁创作的、画面描绘谁、馆藏对象归属谁、文件能否公开使用是四个问题，不能压成一个 `author`。没有可靠肖像时，可以选择手稿、器物或地点作 hero；publish-ready 必须阻断权利不明的正式资产。

## 7. 外部核验与模型治理

外部核验的正确路径是：

1. 找到可独立复查的来源与 locator。
2. 新增或补强 Source Unit 和 Observation。
3. 创建 `ExternalVerification`，连接 sources 与 Canonical targets。
4. 如事实结论需要变化，另走 admission / resolution，由正式 reviewer 签署。
5. Canonical、Source Unit 与 verification 建立双向反链。

GLM-5.3 或其他外部模型适合并行完成来源候选整理、缺口扫描、冲突比较与修订建议。它们的产物一律是 `recommendation_only`，必须保留模型、任务、输入范围和建议引用，且不能成为 formal review。正式签署者只能是 manifest allowlist 中的 `human` 或 `main_agent`；伪装成人名的模型 reviewer 同样会被门禁拦截。

## 8. Audit 与 Verify

### 8.1 单人物审计

```bash
python scripts/biography_store.py audit \
  --store-root ./biography-data/sample-scholar \
  --mode audit

python scripts/biography_store.py audit \
  --store-root ./biography-data/sample-scholar \
  --mode strict-data --json

python scripts/biography_store.py audit \
  --store-root ./biography-data/sample-scholar \
  --mode publish-ready
```

- `audit`：迁移盘点。只有 fatal 返回失败码；非 fatal 缺口仍完整报告，不能把结果描述为“已合规”。
- `strict-data`：要求 v2 manifest、治理账本、六类 Canonical、证据/解释/核验闭包、redirect、关系、历史资料语义与资源隔离全部成立。内容可以稀疏，但不能不诚实。
- `publish-ready`：完整执行 strict-data，再要求 publication 与 Editorial 达到发布状态。

### 8.2 编译/导出前验证

```bash
python scripts/biography_store.py verify \
  --store-root ./biography-data/sample-scholar \
  --phase compile

python scripts/biography_store.py verify \
  --store-root ./biography-data/sample-scholar \
  --phase export --json
```

`verify` 与 `audit` 调用同一 `audit_store()` 谓词。compile/export 不允许各自维护一份删减版检查：

- legacy store 可在迁移期间继续读取，但 fatal 仍阻断。
- v2 draft 空骨架可以初始化和迭代。
- v2 一旦进入有内容的 draft，compile 至少达到 strict-data。
- review/published 以及正式 export 必须达到 publish-ready。

退出码 0 只说明被声明的结构与闭包成立，不代表所有历史解释已经穷尽。高风险事实、争议和译文仍需人工语义复审。

## 9. 跨人物隔离与 corpus 审计

每个人物必须拥有独立：

- store 根、slug、ID namespace 与稳定 subject ID；
- Canonical / Editorial 文件映射和治理账本；
- route base、asset base、asset target 与包含 slug 的 CSS scope；
- Source↔Observation↔Decision↔Canonical↔Verification 闭包。

共享资源只有在 manifest 中声明 `owner=biography-series`、`read_only=true`、`@series/` 引用和 SHA-256 时才可跨人物复用。另一个人物的路径、人物 ID、CSS selector、资产目录或 reviewer 不得成为隐式默认值。

批量检查使用：

```bash
python scripts/biography_store.py audit-corpus \
  --corpus-root ./biography-data \
  --mode strict-data --json
```

`audit-corpus` 除逐人物运行同一审计外，还检查 slug、namespace、路由、资源目标和 Canonical ID 的跨 store 冲突。新增第二个人物前先跑一次，批量发布前再跑一次。

## 10. 源码级 Python API 与宿主适配器

稳定、面向使用者的正式入口是 `scripts/biography_store.py` CLI。本仓当前不发布 PyPI 包；下面这些函数属于源码级 API。需要嵌入自有编译器时，从 `scripts.biography_contract` 导入，并把依赖固定到明确的仓库 tag：

- `manifest_v2_skeleton(...)`：生成新人物 v2 manifest 骨架。
- `normalize_manifest(...)`：给迁移期消费者提供受控的 v1/v2 兼容视图。
- `audit_store(...)`：单人物统一语义审计。
- `audit_corpus(...)`：跨人物冲突与逐 store 审计。
- `assert_store_ready(...)`：compile/export 前 fail-closed 门禁。

宿主可以写薄适配器处理本地路径，但不得复制或改写谓词。Schema registry 的定义名、Python registry 与测试 fixture 必须一一对应；改规则后应同时增加正例、反例和 mutation test，确认门禁真的会红。候选期源码 API 不承诺跨 tag 自动兼容，升级时必须先运行宿主回归。

## 11. 完成定义

一个人物资料库只有同时满足下列条件，才可交给发布层：

- source、observation、decision、canonical、verification 的双向证据链闭合；
- 所有正式裁决由 allowlist reviewer 签署，模型只保留 recommendation；
- 日期、版本、姓名、争议、引语和媒体权利没有被压平成不真实的通用字段；
- 单人物 `publish-ready` 通过，整个 corpus 的 `audit-corpus --mode publish-ready` 也通过；
- projection 可由源数据确定性重建，且下游没有反写事实层。

任何一项未满足，都应继续处于 draft/review，而不是靠降低门禁或删除争议来“发布成功”。
