# 变更记录 - knowledge2skills

本文件记录本项目的重要变更。

## [1.4.1] - 2026-03-28

### 新增
- 新增对 `content_list` / `content_list_v2` 这类结构化 JSON 解析结果的原生提取支持。
- 新增对标题、正文、表格、公式、图片 block 的 typed section 展开能力。
- 新增页码和章节路径保留逻辑，让结构化 JSON 进入下游图谱时上下文更完整。

### 调整
- `.json` 输入不再优先走简单的 `json.dumps(...)` 退化路径，检测到结构化 content list 时会走 parser-aware 提取。
- 更新 README、README_CN 与技能说明，作为 3 月 28 日的质量升级版发布。

## [1.40] - 2026-03-21

### 修复
- 修复 `.mobi` 与 `.azw3` 提取逻辑，改为读取解包后的真实正文，而不是把提取路径当内容。
- 修复流水线领域检测接线错误，改为正确调用异步领域检测函数。
- 修复 OpenAI 兼容图查询流程，embedding 维度现在会从打包后的图数据库中读取，而不是假定为 OpenAI 默认值。
- 修复历史图谱的可视化分类逻辑，避免把非文学语料强行映射到文学专用节点类型。
- 修复技能覆盖安装时的回滚问题，安装失败时可恢复旧技能。
- 增加仓库忽略规则，避免 `.DS_Store`、`__pycache__` 与字节码文件污染版本库。

### 新增
- 新增独立图片 / 地图输入支持，覆盖 `.png`、`.jpg`、`.jpeg`、`.webp`。
- 为 LightRAG 新增 OpenAI 兼容 provider 支持，可通过 `OPENAI_API_BASE` / `OPENAI_BASE_URL`、自定义聊天模型和 embedding 模型完成接入。
- 为历史 / 学术语料新增图谱抽取提示词加固与示例。
- 新增本地 MinerU 超时环境变量 `KNOWLEDGE2SKILLS_MINERU_TIMEOUT`。
- 完成 README 与 changelog 的中英文同步更新。

### 调整
- 根据 3 月 21 日真实生产调用结果，更新项目文档、技能说明与工作流建议。

## [1.3.0] - 2026-03-20

### 新增
- 新增 `scripts/semantic_engineering.py`，用于高级知识密度分析。
- 引入 SKU（标准化知识单元）体系，从简单分段转向结构化知识拆解。
- 新增语义密度评分，可自动识别文档中的高价值“知识挖掘区”。
- 增强生成的 `SKILL.md`，加入语义密度亮点和知识单元摘要。

## [1.2.0] - 2026-03-17

### 新增
- 打通 Graph RAG 闭环，把 `scripts/query_graph.py` 直接打包进技能，支持可执行的关系推理。
- 强化 `SKILL.md` 生成逻辑，加入“Graph-First”子智能体指导。
- 支持把 `graphml` 与 `json` 图数据库完整打包进技能包。

## [1.1.0] - 2026-03-17

### 新增
- 初步集成 EvoMap，支持 GEP-A2A 协议的技能分发场景。
- 集成 MinerU（Magic-PDF），用于复杂版面高精度解析。
- 标准化交互式 HTML 图谱浏览器。
- 支持按领域自动选择实体类型模板。
- 支持智能实体合并与别名管理。
- 支持中英意等混合语料处理。

## [1.0.0] - 2026-03-17

### 新增
- 核心引擎首个稳定版本发布，项目由 `anything2skills` 演化而来。
- 支持 PDF、DOCX、EPUB、MOBI、AZW3、Markdown、TXT、JSON 的统一提取。
- 原生支持 Ollama 本地后端。

## [0.8.0-beta] - 2026-03-15

### 新增
- 首次实验性集成基于知识图谱的 LightRAG。
- 初步支持 `.mobi` 与 `.epub`。

## [0.5.0-beta] - 2026-03-09

### 新增
- 扩展支持 `.docx` 与 `.md`。
- 引入基于文档领域的 `low / medium / high` 自由度。

## [0.1.0-beta] - 2026-03-07

### 新增
- 项目概念期，最初名为 `pdf2skills`。
- 使用 `pdfplumber` 实现基础文本与表格提取。

---
作者：Leo Yuan Tsao ([@yuancafe](https://github.com/yuancafe))
