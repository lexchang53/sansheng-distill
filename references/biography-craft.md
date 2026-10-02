# biography_corpus -- 人物生平蒸馏与可追溯资料库

限定某一思想/事件/时段的任务先读 [person-topics.md](person-topics.md)，仅复用本文件的适用阶段，不要求完成全传。

这条路径把人物的传记、自述及补充资料归并为完整、细节丰富、可回查的人生叙事与数据资料库。默认服务普通读者；学术考证、原典校勘和教材级事实审查只有在任务明确要求时启动。

> 当前数据契约为 `0.9.0-candidate`，与仓库 SemVer 分开管理。源码 API 使用者应固定明确 tag；正式形状与闭包仍以 schema 和统一审计器为准。下文调整生产与取证尺度，不改变机器契约。

## 0. 路由、质量与工作尺度

| 目标 | 应走路径 |
|---|---|
| 单独蒸馏一本书或一组视频 | 按 SKILL.md 书籍定档；视频走作品主管线 |
| 归并一个创作者自己的跨媒介观点 | `creator_corpus` |
| 用多本传记、本人作品及补充资料讲完整个人生平 | `biography_corpus`（本文件） |
| 企业沉浮、经营机制、财务与控制权研究 | 企业研究能力主导；其中单本书层可复用书籍蒸馏路线 |
| 页面、SEO、站点工程与部署 | 下游产品/网站能力 |

同一人物的多本书作为生平材料时走本路径，不要求先为每本书完成一套独立书页。独立书籍、视频、创作者思想蒸馏及企业研究的核验要求不因本文件调整。

### 0.1 默认质量：书本可靠、人生完整、故事有细节

以覆盖生涯的成熟传记作骨架，用本人自述、作品和其他传记补充。普通生平内容可直接据已读出版物整理，并保留书目与章/节/页定位；**出版物足以作为来源，不默认再追原信、原刊或档案书影**。书籍也可能出错，但有限的材料误差不应演变为逐条历史考证。可靠网页、机构简介及通行知识可补缺，注明实际使用的出处；不把模型记忆、搜索摘要或多站转载当作已读材料或独立佐证。

交付重点是完整人生、重大转折、关系与日常、行动过程及后果、连续可读的中文叙事。避免明显错误、主动编造、主体错置和把推测写成确定事实；不要求穷尽所有解释、消灭细小日期差异或为普通事实机械增加第二、第三来源。史料已由可靠书籍转引时可以据书使用，标明来源层级，不宣称自己核过原件。

### 0.2 高保留：尽量保住每本书 70%–80% 的实质内容

人物生平蒸馏默认以 **70%–80% 的故事与实质信息保留**为目标，保留经历、关系、过程、日常、行动细节、转折、后果、人物感受及重要的作者解释。比例不指原文字数、逐字引用量、输出长度或被模型命中的段落数，也不要求到 80% 就删去有价值材料。用自己的中文重述与重组，必要短引注明出处，版权原文和底本留在私有资料区。

下载的书先盘点可读性、版本与覆盖范围；纳入本轮实际蒸馏的每本书都列入保留对照。重复版本、残缺不可用本或与人物生平无关的书说明理由另列，不能为了提高比率把难处理或有异说的正文排除。

同一人物的不同书可以把同类事件合成一个场景，调整章序与叙述次序；各书的定位仍回到这个合并场景。**合并的是重复叙述，不能顺带丢掉各书独有的动作、人物互动、环境、困难、选择和余波**。重要异说、立场与视角差异保留归属，不拼成全知叙述。共同信息在合并场景中真实呈现并分别回链，可计入各书的保留；各书独有信息须另外实际呈现，不能只凭共同事件名算覆盖。信息只留在私有索引或标成 hold，不算正文保留。

默认按书的章/节与其中主要故事单元做一次保留对照，列「保留/合并到哪里、未保留及原因」；前言、目录、索引、重复说明等非实质部分说明范围。无需先对全书每个自然段建账、逐句签审才开写。重要转折和高密细节章不能被全书平均比例掩盖；估计须说明已处理章/节、主要故事去向和未保留内容，并回读代表性高密章验证，不能凭“每章都有一条标签”报约 75%。未统计独立信息单元时只报告有依据的覆盖估计及缺口，不编造精确百分比。明显低于目标或一章被压成几句年表时回书补故事，而不是填字数。

### 0.3 生产顺序与验收

1. **盘书、读书**：优先现有可读电子书；缺核心书时调用可用取书能力，取后查版本、正文完整性和可读性。优先可提取版本；扫描本做足以支撑阅读的 OCR，遇乱码、缺页或关键字不明才定点回书影。
2. **按书提取、按人生归并**：顺原书章/节读完整故事，保留长场景素材与定位，再跨书合并。场景保留时间、参与者、动作、困难、选择、结果及感受的来源；不把原料先压成短摘要。模型可分章并行抽取、拟写和查漏，主审核来源忠实度、声音归属及重大冲突。
3. **先推进完整全传，再集中补缺**：用有支撑的材料写到生涯终点，章级复核随写进行。可用代表性章节校准风格，但不将两章样章的原件齐备或独立签署设为所有全传写作的通用前置条件。未解小项局部收敛表达或列待补，不冻结其他章节。
4. **整体验收与交付**：对照各书检查故事细节与保留目标，通读人生主线、相邻章和关系变化；修明显错误、重复、漏写和无据强断言。下游需数据库时同步入库与重建投影，跑适用的数据及实际页面检查。进展按已完成章节/人物与读者可见内容报告，不以候选数、签名数或核过多少原件代替作品完成。

按章/节记录定位、合并与未决事项即可开始生产。正式 store 中已写入的 Observation、裁决、正文审阅及投影仍按现行机器契约保存，可批次生成账本；不为追求效率伪造审核或降低代码门禁。工程校验管引用和闭包，不能被解释成“每个事实都须独立原件佐证”。

### 0.4 何时加查，何时停止

只对会改变人物理解的重大冲突、明显可疑的关键事实、严重指控、强因果或重要引语归属定向查证。先回读所用书的整段和相邻章，再找另一部可靠书或适当网页；确有必要且取得成本合理时才追原始材料。小日期差异可写年份/时期，不假造精确月日。

一轮指回读相关书段并做一次针对性的补充来源检查，不把无限换词/换入口都算同一轮。没有实质进展，就作局部裁决：采用可靠来源的有归属说法、并列重要异说、缩小断言或略去非核心细节。只有出现具体新线索，或用户明确要求考证，才继续追索；不反复请求同一失败原刊入口。核心经历确无可靠材料时补来源或明确留白，不让边缘项无限拖住全传。

本人回忆、他人转述、传记作者解释与编辑归纳按需要标明，尤其是心理和对白。不要删光可靠书里的感受与故事细节；可写“她后来回忆”“某传记记述”，不把文学化转述冒作同期逐字记录。未听原录音时据书或馆方转录写，不描述音色、停顿或掌声；没有使用音轨细节就不要求整段音频核听。

## 1. 单向证据链与必要回查

```text
Source Unit -> Observation -> MergeDecision -> Canonical -> Editorial -> Projection
     |                                        ^
     +-> ExternalVerification ----------------+
```

- **Source Unit**：具体书籍版本、文章、网页或馆藏对象。普通生平的书中定位就是有效证据入口。
- **Observation**：来源在明确 locator 上支持的主张，事实、作者解释与未知状态分开。
- **MergeDecision**：正式 reviewer 对接纳及 Canonical 写入方式的裁决。
- **Canonical**：跨来源合并后的 People、Events、Works、Relations、Controversies、Quotes。
- **ExternalVerification**：风险触发的额外复核，须反链来源与目标；不要求每个普通主张都有一条。
- **Editorial**：章节、概览等叙事选择，可据来源重组故事，不能创造事实。
- **Projection**：给消费者的只读输出；页面状态不反写事实层。

提取不能用极短字段上限或固定少量候选切掉素材。保留可回读的私有长段/场景索引；本人文字与编者、记者、机构叙述分开，书信不跨收信人合为一封。输出上限触及时补遗漏部分，不把满额回文当作读完一本书。模型回文的 `completed`、JSON 完整或行号命中只证明接口/定位有效，不是内容验收或保留率。

扫描本的 PDF 页、印本页和 OCR 行号分别记录。模型主体、日期、代词、跨页接续有疑点时回整段或原页；可读文字无异常时不要求逐页与书影重校。年谱按实际年份和事件检查漏年，一段内多次迁居、任教或创作分别保留，不因模型遗漏而推断当年无事。

发布人物返工先看真实页面及相邻章，再查已冻结书源的目录与全文。乔布斯 Apple II、Pixar 与 Macintosh 曾出现“只看所选源段便断言书中未载”的误判；应补原书已有的过程与因果桥，不增加无关取证。修复受影响的来源、裁决、正文与投影，完成范围据实报告。

更高强度的研究任务可以冻结逐段分母、逐项核原件并留去向收据，但须明确目的与范围；不把这套账本自动推广为所有人物的生产前置条件。正式 source coverage 仍按实际使用范围签署，不将下载、候选或 hold 算作已保留。

长期任务交接留下当前章节与里程碑、输入哈希、底本位置、未决项及下一步；区分候选、本机提交、远端主线和网站上线。快照明确不含哪些底本，接手先核现场，不按旧收据覆盖新文件。

JSON Schema 验单文件形状；`scripts/biography_contract.py` 验跨文件闭包，CLI 与宿主共用，不另造近似判据。机器通过不证明所有历史解释已经穷尽，普通书本蒸馏也不因缺少无关原件被阻塞。

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

外部核验由 §0.4 的重大风险触发，普通书中事实不逐条另查；需要执行时，路径是：

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
