# 旧书重蒸：整包迁移、索引替换与科学终审

首次蒸馏沿主管线；替换已有正式书时先用本契约。旧页存在、旧报告为绿或新正文生成，都不能证明整书升级完成。内容级验证通过与发布完成分别登记。

## 1. 迁移清单与实际依赖

列出项目的实际消费者。来源原件/文本、冻结知识分母、正文、来源审计、章节映射、概念清单、设计/封面、聚合及项目投影，逐项选择 updated、preserved、archived、not_applicable 并说明依据。不把某项目的文件名写成所有书必需；项目声明自己的 required_roles。未声明迁移清单的历史书不由新检查器自动拒绝。

清单格式：`schema: distill-upgrade-v1`，`book_slug`，`content_sha256`，`required_roles`，`artifacts[]`。每个 artifact 有唯一 `role`、相对 `path`、真实文件 `sha256`、`action`；非 updated 需 `reason`。source/content 必须是活跃必需角色；content 是最终 distill.json。其他活跃角色必须带当前 `content_sha256` 和非空 `inputs_sha256: {依赖角色: 文件SHA}`。归档数据不能当作活跃依赖，依赖不能成环。

preserved 还需 `previous_path`、`previous_sha256`，机器验证前后文件同字节；这仅证明产物没变，审阅签署复用仍需任务、提示、参数、上下文及审阅对象等价。原文改变、分母改变、正文改变的影响按角色依赖追踪，不能只凭支持句 hash 继承签署。

若消费者 JSON 已含来源/成员 SHA，用 `json_bindings: {"/source_sha256":"source"}` 之类的 JSON Pointer 检查实际字段。这样，即使有人重记旧文件的 SHA，也无法通过旧来源绑定。没有嵌入绑定的 HTML/设计文件仍需项目语义投影检查；不把清单自述当作消费者一致性证据。

```sh
python3 "$SKILL/scripts/verify_upgrade_manifest.py" "$BOOK/upgrade-manifest.json" --root "$DATA"
```

缺必需输出、旧来源/文件 SHA、旧嵌入绑定、非法路径、空清单必须失败。checked_artifacts 表示核查文件数，不能当成正确知识或上线数量。

## 2. 显式整书索引替换

`register --force` 只替换本次出现概念中的同书 entry，不撤销取消概念的旧贡献。重蒸改用：

```sh
python3 "$SKILL/scripts/update_index.py" replace-book --index "$DATA/knowledge-index.json" \
  --merge "$BOOK/index-merge.json" --distill "$BOOK/distill.json" --book-slug "$SLUG" --dry-run
# 复核差异收据后，同样参数去掉 --dry-run 执行。
```

候选必须非空、只有指定 slug，名称集合与最终 distill.concepts 完全一致，entry 的书名、立场、锚点取最终数据。若语义匹配需统一索引概念名，先在最终 distill 中明确 canonical 名，保留原书叫法作为别名；不能默默漏登记。

先撤本书全部旧贡献，再在候选索引上校验 relation 并登记。旧概念还有他书贡献时保留；仅剩本书且新版取消的普通空概念移除。含额外人工注释字段的空概念保留，不能自动删注释；因此 NEW_CONCEPT 与该保留名冲突仍应拒绝。非 NEW_CONCEPT 的同名概念壳在本次替换保留，允许更新立场。旧有他书 relation 不因删掉本书而重写；它是登记时历史语义，不能被拿来推断新的跨书边。

dry-run 输出 removed/replaced/added 与他书保留数，不写盘。正式执行校验先行、保存 .bak、同目录原子替换；相同语义结果不重写文件。工具用排他锁并比较读取快照，但旧 register 不使用该锁，所以项目必须串行所有共享索引写入；不承诺能保护绕过协议的外部写者。

验收旧 A/B→新版仅 B、他书 A 保留、B 更新、同输入幂等；空/混 slug/缺概念/非法关系/重复名称/错误锚点全部拒绝且不改文件。

## 3. 科学证据终审收据

心理学科学层在既有 evidence_page 与 source-audit 之外，补独立终审收据。它校验访问与裁决记录的完整性，不能自动确认论文真实性、引文忠实度或科学结论。

格式：`schema: distill-science-review-v1`，`book_slug`，`inputs_sha256: {distill: SHA, enrich: SHA}`，`claims: {claim_id: review}`。键集合与 core_ideas/decision_rules 全部唯一 claim_id、evidence_page.claims 完全相等；空分母拒绝。

每条 review 含 `status: reviewed`、主控实际 `reviewer`、ISO 日期 `reviewed_on`、裁决理由 `conclusion`、`sources[]`。没有完成主控回源时留 pending，禁止模型自己签 reviewed。每个 source 以与 evidence_page 精确相等的 `url` 对应，含：

- `access_level` 和相同的 `locator_basis`：publisher_full_text、author_manuscript、preprint、abstract、official_material；按实际读到的层级填写。
- `checked_on`、`locator`（页/节/表/摘要句等准确位置）、`support`、`scope_limit`、`correction_check`。
- `metadata: {title, year, authors, doi?}`；title/year 与证据卡精确一致，DOI 若多处提供须正规化后一致。
- `support_excerpt` 和其 UTF-8 SHA-256 `support_sha256`，供私有审阅回溯。只保存足够裁决的短句，不把整篇研究全文或版权书复制进公开 Skill。若公开分享收据，另行逐源核引用许可/限额。

not_testable 可以无来源，但 review 需 `nonempirical_reason`。摘要或作者稿不自动排除 supported，结论只覆盖实际可证实的主张；严禁冒称已读全文。不强凑 supported/mixed/contested/not_supported 分布。研究 effect/样本/时域边界放 scope_limit 与现有科学卡 scope 中，由主控核一致。

```sh
python3 "$SKILL/scripts/verify_science_review.py" "$BOOK/science-review.json" \
  --distill "$BOOK/distill.json" --enrich "$BOOK/enrich.json"
```

有 URL 无定位、访问层级与定位依据冲突、混 DOI、来源/claim 缺项、摘要句被改而 hash 未变、旧输入 SHA、pending 都必须失败。结构通过仍继续实际消费者与阅读验收，不标自动科学正确或已上线。

## 4. 交付边界

共享 Skill 负责内容版本、产物 SHA、角色依赖和锚点；网站适配器负责语言投影、聚合消费者、SEO、构建名额与真实发布收据。正式包和共享索引由主控写入；模型只产私有候选。每书记录来源放行、分母冻结、正文审阅、科学终审、整包一致、进入主线、发布成功、公网核验，不能合成一个笼统 done。
