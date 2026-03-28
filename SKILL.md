---
name: knowledge2skills
description: Transform any source material (PDF, MD, TXT, DOCX, EPUB, MOBI, AZW3, JSON, images) into structured, executable AI skill packages. Specializes in Knowledge Production using LightRAG for graph-enhanced precision, OpenAI-compatible providers, and bundled graph databases. "knowledge2skills", "docs2skills", "ebooks2skills", "把这些文档变成技能", "知识生产流水线".
---

# knowledge2skills — Advanced Knowledge Production Pipeline (v1.4.1)


## Overview

`knowledge2skills` is an advanced evolution of knowledge production, designed to convert unstructured information from multiple sources and formats into structured, executable AI skill packages. It prioritizes **Graph-Enhanced Precision**, **Multi-source Synthesis**, and **Self-contained Deployment**.

## Core Capabilities

1.  **Multi-format Extraction**: Seamlessly processes `.pdf`, `.md`, `.txt`, `.docx`, `.epub`, `.mobi`, `.azw3`, `.json`, and standalone images/maps.
2.  **Structured JSON Ingestion**: Expands parser outputs such as `content_list.json` into typed sections for text, tables, equations, images, and headings instead of flattening them into one raw blob.
3.  **Cross-lingual Synthesis**: Built-in support for mixed-language inputs (Chinese, English, Italian, etc.). It creates unified knowledge structures where concepts across different languages are mapped and linked.
4.  **Batch Synthesis**: Combines multiple files (e.g., a series of history books) into a single unified skill with source-aware sectioning.
5.  **OpenAI-Compatible Graph Construction**: Supports OpenAI-compatible endpoints through configurable `OPENAI_API_BASE` / `OPENAI_BASE_URL`, including providers such as OpenAI, NVIDIA-compatible endpoints, DashScope, and other compatible gateways.
6.  **Domain-Adaptive Graph RAG**: Integrates advanced logic from `rag-builder` to automatically detect document domains and apply optimized entity types (e.g., Medical, Legal, Business). It learns and updates these types over time.
7.  **Smart Entity Deduplication**: Automatically merges similar entities (e.g., "Dante" + "Dante Alighieri") during graph construction to ensure a clean and accurate knowledge base.
8.  **Interactive Graph Visualization**: Generates a self-contained, web-based interactive graph explorer bundled within the skill (`references/visualization/index.html`).
9.  **Auto-Configuration & Setup**: Scans the environment for LightRAG and necessary keys. If missing, it provides interactive installation and configuration prompts.
10.  **Bundled Graph DB**: If built, the LightRAG database is bundled into the skill package (`references/graph_db/`) for high-fidelity secondary retrieval.
11.  **Historical-Domain Hardening**: Graph extraction can bias toward grounded historical entities and relationships when the source material is historical or scholarly.

## Workflow

1.  **Extract**: `scripts/extract_content.py <file1> <file2> ...` — Multi-file parallel extraction.
2.  **Graph (Optional)**: `scripts/lightrag_graph.py` — Builds a persistent knowledge graph.
3.  **Produce**: Generates a skill directory containing `SKILL.md`, `references/`, and `scripts/`.
4.  **Install**: Registers the skill in `~/.agents/skills/`.

### One-Command Full Pipeline
```bash
python3 scripts/knowledge2skills_pipeline.py book1.pdf book2.md --name history-expert --graph --install
```

## Sub-agent Guidance

*   **API Check**: Before running the graph enrichment, check for `OPENAI_API_KEY`. If missing, prompt the user.
*   **Graph Retrieval**: If a skill contains a `references/graph_db/` folder, prioritize using `LightRAG` queries over simple text search for complex "how" and "why" questions.
*   **Source Attribution**: Maintain the `[Source: filename]` prefixes in extracted sections to ensure traceability.
*   **Provider Config**: When the user provides a non-OpenAI endpoint, pass through `OPENAI_API_BASE` or `OPENAI_BASE_URL`, `LIGHTRAG_LLM_MODEL`, and `LIGHTRAG_EMBEDDING_MODEL`.

## Dependencies

- `pdfplumber`, `pypdf`: PDF parsing.
- `python-docx`: DOCX support.
- `lightrag-hku`: Knowledge graph building.

## Documentation

Detailed usage is available in **[api_reference.md](references/api_reference.md)** and **[extraction_guide.md](references/extraction_guide.md)**.
