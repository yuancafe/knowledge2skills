# 🚀 knowledge2skills (又名 docs2skills)
**工业级 AI Agent 知识生产流水线。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![RAG: LightRAG](https://img.shields.io/badge/RAG-LightRAG-orange)](https://github.com/HKUDS/LightRAG)

---

## 🌟 项目概览

**knowledge2skills** 是一套先进的自动化知识生产流水线，旨在将非结构化的法律、学术、技术文档（书籍、论文、手册、笔记）转化为**结构化、可执行的 AI 技能包**。

不同于传统的简单检索（RAG）系统，本流水线侧重于**“知识生产”**：通过提取核心方法论、系统逻辑和层级化工作流，为您的 AI Agent 构建一个自包含的“专家大脑”。

---

## 🔥 核心功能

- **🔍 高精度解析 (MinerU)**：集成 **MinerU (Magic-PDF)** 支持。针对复杂排版、数学公式和科学表格提供卓越的解析能力。
- **🧠 图谱强化 (LightRAG)**：构建知识图谱，精准识别非线性关系和复杂的系统反馈回路。
- **⚡ 混合检索架构**：结合 **图谱 RAG、向量搜索与全文搜索**，实现对文档的多维深度理解。
- **📊 交互式可视化**：每个技能包内置自包含的 Web 端图谱浏览器，方便直观探索知识关联。
- **💻 本地优先 (Ollama)**：原生支持 **Ollama**。无需 API 密钥即可在本地完成大规模知识库构建，零成本，隐私安全。
- **🌍 跨语言合成**：支持中、英、意等多语种混合输入，生成的技能支持全语种自适应交互。
- **🤖 Agent 深度优化**：生成的 `SKILL.md` 包含针对 AI 子智能体的“外科手术式检索”与“证据溯源”指令。
- **📦 全格式 & 批处理**：支持 PDF, DOCX, **EPUB, MOBI, AZW3**, MD, TXT, 和 JSON 的批量合成。

---

## 🛠️ 使用指南

### 1. 安装
```bash
# 克隆仓库
git clone https://github.com/yuancafe/knowledge2skills.git
cd knowledge2skills

# 安装核心依赖
pip install lightrag-hku pdfplumber pypdf python-docx ebooklib beautifulsoup4 mobi psutil
```

### 2. 基础用法 (一键流水线)
运行编排脚本处理您的文件：
```bash
python3 scripts/knowledge2skills_pipeline.py <文件1> <文件2> --name <技能名称> --install
```

### 3. 高级指令与参数
| 参数 | 描述 |
| :--- | :--- |
| `--graph` | 开启 LightRAG 知识图谱构建。 |
| `--viz` | 生成交互式 HTML 可视化图表。 |
| `--dedup` | 运行智能实体去重与合并。 |
| `--high-precision`| 使用 **MinerU** 处理复杂 PDF。 |
| `--force` | 强制覆盖目标目录中的现有技能。 |
| `--install` | 自动将生成的技能注册至 `~/.agents/skills/`。 |

#### 示例：构建一个专业的历史知识大脑
```bash
python3 scripts/knowledge2skills_pipeline.py 卷1.epub 卷2.pdf 笔记.md \
    --name history-expert \
    --graph \
    --viz \
    --dedup \
    --high-precision \
    --install
```

---

## 🎨 领域自适应

流水线会根据内容领域自动调整提取策略：
*   **低自由度**：金融、数据科学（强调数学精准度，生成 Python 脚本）。
*   **中等自由度**：求职、经济、环境、技术。
*   **高自由度**：心理学、哲学、历史、复杂科学（强调系统性思维，生成概念图谱）。

---

## ⚙️ 环境要求与 API

- **OpenAI API**: 如果使用云端图谱 RAG，需要配置 `OPENAI_API_KEY`。
- **Ollama**: 如果检测到 Ollama，系统会提示使用本地模型（零成本）。
- **硬件建议**: 使用 MinerU 高精度解析时，建议内存 8GB+，磁盘空间 10GB+。

---

## 📂 项目结构

```text
knowledge2skills/
├── SKILL.md                # 技能定义模板
├── scripts/
│   ├── knowledge2skills_pipeline.py # 一键编排脚本
│   ├── extract_content.py           # 多格式统一提取器
│   ├── lightrag_graph.py            # 图谱 RAG 集成逻辑
│   ├── generate_skill.py            # 技能包生成器
│   ├── generate_visualization.py    # HTML 图谱构建器
│   └── entity_deduplicator.py       # 智能实体合并器
└── references/
    ├── extraction_guide.md          # 领域提取策略指南
    └── api_reference.md             # 脚本 API 文档
```

---

## 👤 作者

**Leo Yuan Tsao**  
GitHub: [@yuancafe](https://github.com/yuancafe)  
*专注于 AI 驱动的知识生产与 Agent 架构研究。*

---

## 📄 许可
MIT License.
