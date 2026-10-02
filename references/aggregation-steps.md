# aggregation-steps.md — 可选聚合步骤：StepA 作者演变 / StepB 主题聚合

> 自 `SKILL.md` 迁入，**内容未改**。两者都只读已蒸书的 `distill.json`，**绝不重蒸**；<2 部（StepA）/ <3 本（StepB）不生成。
> 类别总览（心理学、管理学等“总—分”书目入口）见 `category-framework.md`，不在这里。

## StepA · 作者演变聚合(可选,同一作者 ≥2 部已蒸时)

某作者在 `$DATA` 下已蒸 **≥2 部**作品时,可选做「思想演变专题」聚合页;单书蒸馏不涉及,**<2 部不生成**。

- **做什么**:只读各书 `distill.json`(**绝不重蒸**)聚合成 `author.json` → 渲染作者演变页 `author.html`(4 视图:时间线 / 母题 ribbon / 思想转向 / 概念演化图)。每书蒸馏页顶部「演变入口卡」(SLOT:AUTHOR-ENTRY)链到它。
- **读哪个 reference**:`author-craft.md`(§0 事实 vs 叙事铁律 / §2 author.json schema / §4 四视图数据契约 / §5 板块骨架 / §6 转向证伪层 / §7 入口卡)。
- **跑哪条命令**:`python $SKILL/scripts/build_author.py --author "<作者名>" --data-root "$DATA" --manual "$DATA/authors/{author_slug}/author.manual.json" --enrich "$DATA/authors/{author_slug}/author.enrich.json" --out "$DATA/authors/{author_slug}/author.json"`(已有 author.json 且 manual 缺失时防覆盖栏拒跑,确需重建加 `--force`;<2 部 exit 3 不生成);再复制 `templates/author-page-skeleton.html`、把 `#author-data` 槽替换为该 `author.json` 生成 `author.html`。
- **产物**:`$DATA/authors/{author_slug}/author.json` + `author.html`。
- **显式成员与站内书页**:需纳入合著作品或固定策展边界时,在 manual 写 `member_slugs:[slug]`;清单中任一成员缺失、损坏或内部 slug 不一致即 exit 2,不得静默缩小集合。可在 `book_meta.{slug}.web_url` 写站内根相对书页路径(如 `/library/work-a.html`);只接受安全的单 `/` 起始路径,非法值不进入产物。
- **触发门槛 / 降级**:该作者 <2 部已蒸 → `build_author.py` exit 3 不生成、连网搜(enrich)不启、每书页入口卡整卡删。
- **出厂验证**:`python $SKILL/scripts/verify_page.py "$DATA/authors/{author_slug}/author.html"; echo "退出码=$?"`(自动识别作者页走独立门禁:4 视图齐 / 零外链 / Zero-Hex / lang=zh / 破折号 / slug 与 `web_url` 安全 / 转向 verdict 一致;exit 0 才算完成)。

## StepB · 主题聚合(可选,同主题 ≥3 本已蒸时)

同一主题下已蒸 **≥3 本**作品时,可选做「主题聚合专题」页 -- 把各书按流派归类、把分歧摆上台面、把可执行数字并排对照。单书/双书不涉及,**<3 本不生成**。StepA 聚合「同一**作者**的思想**演变**」(时间轴);StepB 聚合「同一**主题**下各书的**立场光谱与分歧**」(空间轴),对称迁移非照搬四视图。

- **做什么**:只读各书 `distill.json` + `knowledge-index.json`(**绝不重蒸**)聚合成 `topic.json` → 渲染主题聚合页 `topic.html`(4 视图:分类地图 / 分歧矩阵 / 维度对照表 / 书目导航)。每成员书蒸馏页顶部「主题入口卡」(SLOT:TOPIC-ENTRY)链到它。
- **读哪个 reference**:`topic-craft.md`(§0 事实 vs 归纳分层铁律 + 成员圈定 / §2 topic.json schema / §4 四视图数据契约 / §5 板块骨架 / §6 外部争议 enrich / §7 入口卡)。
- **跑哪条命令**:先手写 `$DATA/topics/{topic_slug}/topic.manual.json`(圈定 `members:[slug]` + schools 流派归类 + disputes 分歧分组 + dimensions 维度对照 + verdict 怎么选);再 `python $SKILL/scripts/build_topic.py --topic "<主题名>" --data-root "$DATA" --manual "$DATA/topics/{topic_slug}/topic.manual.json" --out "$DATA/topics/{topic_slug}/topic.json"`(已有 topic.json 且 manual 缺失时防覆盖栏拒跑,确需重建加 `--force`;<3 本 exit 3 不生成);再复制 `templates/topic-page-skeleton.html`、把 `#topic-data` 槽替换为该 `topic.json` 生成 `topic.html`。
- **产物**:`$DATA/topics/{topic_slug}/topic.json` + `topic.html`。
- **成员圈定 = manual 显式列 slugs**:主题边界是编辑判断,不改 distill schema、不自动按 tag 归堆(见 topic-craft §0);清单中任一成员缺失、损坏或内部 slug 不一致即 exit 2,不得静默缩小集合。`book_meta.{slug}.web_url` 与 StepA 同样只允许安全的站内根相对路径。
- **分歧与平行对照分流**:分歧矩阵只渲 `CONTRADICTS`(knowledge-index 已登记真对立,红旗)和 `curated`(编者归纳、金标,`note` 须给依据)。相关但不互斥、回答不同层次问题的材料写入独立 `parallel_comparisons[]`,至少两列且每列均有可回指成员与非空 `stance`,渲染为 `.cmp-card`,不计入分歧数;旧 manual 的 `disputes[].parallel:true` 会迁移到该独立数组。未显式声明、仅被算法判为 `parallel` 的松散并列仍剔除不渲。**编者归纳出 index 未登记的真分歧轴时,应回补进 knowledge-index**。
- **触发门槛 / 降级**:有效成员 <3 → `build_topic.py` exit 3 不生成、每书页入口卡整卡删;`external_debate` 整块搜空 → 该板块隐藏,分类/分歧/维度作书内事实照发。
- **出厂验证**:`python $SKILL/scripts/verify_page.py "$DATA/topics/{topic_slug}/topic.html"; echo "退出码=$?"`(自动识别主题页走独立门禁:4 视图齐 / 零外链 / Zero-Hex / lang=zh / 破折号 / slug 与 `web_url` 安全 / index_relation + certainty 枚举 / 分歧与平行对照可回指 / `.dsp-card`、`.cmp-card` 数量精确;exit 0 才算完成)。
