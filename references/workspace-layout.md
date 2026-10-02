# 路径、数据布局与按需依赖

仅在准备落盘、初始化或遇到依赖错误时读取。人物库按其路线目录；下列是书籍/视频的布局。

## 路径与变量约定(全文只定义一次)

| 占位符 | 展开为 |
|---|---|
| `$SKILL` | 本次实际加载的 Skill 本体目录；从入口解析，不固定某客户端路径 |
| `$DATA` | 项目数据根；优先已有项目约定，再取 `DISTILL_DATA_DIR`，未配置时使用 `./distill-data` |
| `{slug}` | 书的 ASCII kebab 短名(如 `jinqian-xinlixue`);在实际消费者的命名空间唯一，与现有名单机器比对 |
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

## 按需依赖

Python >=3.10，命令显式使用 `python3`；先使用项目已有环境，缺实际依赖再安装，不在人物专题开工时安装整套页面工具。

| 当前动作 | 依赖 |
|---|---|
| epub 转换 | ebooklib、beautifulsoup4 |
| PDF 提取 | pymupdf；仅扫描/异常页需要 OCR 上游 |
| azw3/mobi 转换 | calibre 的 ebook-convert；从实际 PATH 获取，不套用其他系统安装命令 |
| 图片压缩/封面内联 | pillow |
| HTML 动态验收 | playwright 及 chromium |
| biography schema 验收 | jsonschema>=4 |
| YouTube 字幕/评论 | yt-dlp |
| 无字幕、需要画面/声音 | 可用字幕/ASR 或 sansheng-gemini-video；按上游当前接口配置，不假定某环境变量通用 |

pytest 仅开发与测试需要。安装、模型通道和凭证服从所在环境的规则；不在公开 Skill 固化私有路径、模型、并发或账户。
