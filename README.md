# 🚀 knowledge2skills (aka docs2skills)
**The Industrial-Grade Knowledge Production Pipeline for AI Agents.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![RAG: LightRAG](https://img.shields.io/badge/RAG-LightRAG-orange)](https://github.com/HKUDS/LightRAG)

---
Author: Leo Yuan Tsao

English | [中文](README_CN.md)

## 🌟 Overview

**knowledge2skills** is an advanced evolution of knowledge production, designed to convert unstructured human knowledge (Books, Papers, Manuals, Notes) into **structured, executable AI Skill packages**. 

Unlike traditional RAG systems that simply retrieve chunks, this pipeline focuses on **Knowledge Synthesis**: extracting core methodologies, systemic logic, and hierarchical workflows to build a self-contained "Expert Brain" for your AI agents.

---

## 🔥 Key Features

- **🔍 Superior Parsing (MinerU)**: Optional high-precision extraction for complex PDF layouts, mathematical formulas, and scientific tables.
- **🧠 Graph-Enhanced (LightRAG)**: Builds Knowledge Graphs to map non-linear relationships and systemic feedback loops.
- **🧬 Semantic Engineering**: Advanced NLP scoring for **Logic, Entity, and Structural Density**. Identifies high-value "mining zones" for precise knowledge unit (SKU) extraction.
- **⚡ Hybrid Retrieval**: Combines Graph RAG, Vector Search, and Full-text Search for a multi-dimensional understanding of your documents.
- **📊 Interactive Visualization**: Generates a self-contained, web-based graph explorer bundled within each skill package.
- **💻 Local-First (Ollama)**: Native support for Ollama. Build and run your knowledge base locally with zero API costs.
- **🌍 Cross-lingual**: Processes mixed-language inputs (Chinese, English, Italian, etc.) and produces language-adaptive skills.
- **🤖 Sub-agent Optimized**: Automatically generates `SKILL.md` with explicit instructions for "Surgical Retrieval" and "Evidence-based" reasoning.
- **📦 Multi-format & Batch**: Processes PDF, DOCX, EPUB, MOBI, AZW3, MD, TXT, and JSON in batches.

---

## 🛠️ Usage Guide

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/yuancafe/knowledge2skills.git
cd knowledge2skills

# Install core dependencies
pip install lightrag-hku pdfplumber pypdf python-docx ebooklib beautifulsoup4 mobi psutil
```

### 2. Basic Usage (One-Command Pipeline)
Run the orchestrator to process your files:
```bash
python3 scripts/knowledge2skills_pipeline.py <file1> <file2> --name <skill-name> --install
```

### 3. Advanced Commands & Flags
| Flag | Description |
| :--- | :--- |
| `--graph` | Enable LightRAG Knowledge Graph construction. |
| `--semantic` | Enable **Semantic Engineering** (Density scoring & SKU planning). |
| `--viz` | Generate an interactive HTML visualization. |
| `--dedup` | Run smart entity deduplication/merging. |
| `--high-precision`| Use **MinerU** for complex PDF parsing. |
| `--force` | Overwrite existing skills in the target directory. |
| `--install` | Automatically register the skill to `~/.agents/skills/`. |

#### Example: Build a Professional History Brain
```bash
python3 scripts/knowledge2skills_pipeline.py vol1.epub vol2.pdf notes.md \
    --name history-expert \
    --graph \
    --semantic \
    --viz \
    --dedup \
    --high-precision \
    --install
```

---

## 🎨 Domain Adaptation

The pipeline automatically adjusts its extraction strategy based on the content domain:
*   **Low Freedom**: Finance, Data Science (Mathematical precision, Python scripts).
*   **Medium Freedom**: Career, Economics, Environment, Technology.
*   **High Freedom**: Psychology, Philosophy, History, Complex Science (Systemic thinking, conceptual maps).

---

## ⚙️ Requirements & API

- **OpenAI API**: Required if using cloud-based Graph RAG (`OPENAI_API_KEY`).
- **Ollama**: If detected, the pipeline will offer to run RAG locally (0 cost).
- **Hardware**: For high-precision MinerU parsing, 8GB+ RAM and 10GB+ Disk is recommended.

---

## 📂 Project Structure

```text
knowledge2skills/
├── SKILL.md                # Skill definition template
├── scripts/
│   ├── knowledge2skills_pipeline.py # The one-command orchestrator
│   ├── extract_content.py           # Multi-format unified extractor
│   ├── lightrag_graph.py            # Graph RAG integration
│   ├── generate_skill.py            # Skill package producer
│   ├── generate_visualization.py    # HTML graph builder
│   └── entity_deduplicator.py       # Smart entity merger
└── references/
    ├── extraction_guide.md          # Domain strategies
    └── api_reference.md             # Script API documentation
```

---

## 👤 Author

**Leo Yuan Tsao**  
GitHub: [@yuancafe](https://github.com/yuancafe)  
*Specializing in AI-powered knowledge production and Agent architectures.*

---

## 📄 License
MIT License.
