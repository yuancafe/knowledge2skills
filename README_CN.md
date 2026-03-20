# knowledge2skills（又名 docs2skills）
面向 AI Agent 的工业级知识生产流水线。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![RAG: LightRAG](https://img.shields.io/badge/RAG-LightRAG-orange)](https://github.com/HKUDS/LightRAG)

作者：Leo Yuan Tsao

版本：`1.40`
更新时间：`2026-03-21`

[English](README.md) | 中文

另见：[CHANGELOG](CHANGELOG.md) | [中文变更记录](CHANGELOG_CN.md)

## 项目概览

`knowledge2skills` 用来把书籍、论文、手册、笔记和混合格式资料包转成结构化、可执行的 AI 技能。

它重点解决的是：
- 多文件合成
- 带图数据库的 Graph RAG
- OpenAI 兼容模型提供方接入
- 多语种语料处理
- 面向 Agent 的 `SKILL.md` 自动生成

## 1.40 做了什么

`1.40` 是一次基于真实生产调用结果做出来的稳定化版本，发布日期为 `2026-03-21`。

这一版主要修掉了实际使用中暴露出来的问题：
- 修复 `.mobi` / `.azw3` 提取逻辑，改为读取解包后的真实正文，而不是把临时路径当内容
- 新增独立图片 / 地图输入支持，使 `.jpg`、`.png`、`.jpeg`、`.webp` 能进入可查询语料
- 修复流水线里领域检测的异步调用接线问题
- 为 LightRAG 增加 OpenAI 兼容端点支持，可配置 `base_url`、聊天模型和 embedding 模型
- 修复图查询阶段对非 OpenAI embedding 维度处理不正确的问题
- 为历史 / 学术语料增加图谱抽取提示词加固
- 修复可视化类型推断仍按文学模板分类的问题，使历史图谱展示更合理
- 把本地 MinerU 的超时改成可配置，不再固定 30 秒误判失败
- 加固技能安装流程，安装失败时自动恢复旧版本技能

## 核心能力

- 多格式提取：PDF、MD、TXT、DOCX、EPUB、MOBI、AZW3、JSON、独立图片
- 基于 LightRAG 的图谱增强合成
- 面向逻辑、实体、结构密度的语义工程
- 每个技能内置交互式图谱可视化
- 支持通过 `OPENAI_API_BASE` 或 `OPENAI_BASE_URL` 接入 OpenAI 兼容模型服务
- 支持中英等混合语料的跨语言处理
- 自动生成可安装技能包，并打包 `graph_db` 与 `query_graph.py`

## 安装

```bash
git clone https://github.com/yuancafe/knowledge2skills.git
cd knowledge2skills
pip install lightrag-hku pdfplumber pypdf python-docx ebooklib beautifulsoup4 mobi psutil requests pillow
```

## 基础用法

```bash
python3 scripts/knowledge2skills_pipeline.py <文件1> <文件2> --name <技能名> --install
```

## 常用参数

| 参数 | 说明 |
| :--- | :--- |
| `--graph` | 构建 LightRAG 知识图谱 |
| `--semantic` | 运行语义工程与密度分析 |
| `--viz` | 生成交互式 HTML 图谱可视化 |
| `--dedup` | 运行实体去重 |
| `--high-precision` | PDF 优先走 MinerU |
| `--install` | 安装到 `~/.agents/skills/` |
| `--force` | 覆盖已有技能 |

## Provider 配置

云端图谱构建支持 OpenAI 兼容端点。

常用环境变量：

```bash
export OPENAI_API_KEY=...
export OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
export LIGHTRAG_LLM_MODEL=qwen-max
export LIGHTRAG_EMBEDDING_MODEL=text-embedding-v4
```

只要端点与模型名有效，同样的方式也可用于其他兼容提供方。

## MinerU 说明

对于大型扫描 PDF，本地 MinerU 可能运行很久。

现在可以通过环境变量配置超时：

```bash
export KNOWLEDGE2SKILLS_MINERU_TIMEOUT=1800
```

设置为 `0` 可关闭超时限制。

## 项目结构

```text
knowledge2skills/
├── SKILL.md
├── README.md
├── README_CN.md
├── CHANGELOG.md
├── CHANGELOG_CN.md
├── scripts/
│   ├── knowledge2skills_pipeline.py
│   ├── extract_content.py
│   ├── lightrag_graph.py
│   ├── query_graph.py
│   ├── generate_skill.py
│   ├── generate_visualization.py
│   └── install_skill.py
└── references/
    ├── extraction_guide.md
    └── api_reference.md
```

## 来自真实调用的经验

这次 3 月 21 日的真实调用暴露了两个重要事实：
- 图谱质量非常依赖领域提示词和 provider 兼容 embedding 处理
- 图谱“构建成功”不等于技能真的可用，安装、查询、可视化都必须显式验收

## 许可证

MIT
