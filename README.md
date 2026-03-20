# knowledge2skills (aka docs2skills)
Industrial-grade knowledge production for AI agents.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![RAG: LightRAG](https://img.shields.io/badge/RAG-LightRAG-orange)](https://github.com/HKUDS/LightRAG)

Author: Leo Yuan Tsao

Version: `1.40`
Updated: `2026-03-21`

English | [中文](README_CN.md)

See also: [CHANGELOG](CHANGELOG.md) | [中文变更记录](CHANGELOG_CN.md)

## Overview

`knowledge2skills` converts books, papers, notes, manuals, and mixed-format source bundles into structured, executable AI skills.

It is designed for:
- multi-file synthesis
- Graph RAG with bundled graph databases
- OpenAI-compatible model providers
- multilingual corpora
- downstream agent use via generated `SKILL.md`

## What Changed In 1.40

Version `1.40` is the March 21 stabilization release driven by a full end-to-end production run on a difficult historical corpus.

It specifically hardens the workflow in the places that failed in real use:
- fixed `.mobi` and `.azw3` extraction so extracted content is read from the unpacked file instead of treating a temporary path as content
- added standalone image and map ingestion so `.jpg`, `.png`, `.jpeg`, and `.webp` files can become queryable references
- fixed async domain detection wiring inside the pipeline
- added OpenAI-compatible LightRAG support for custom `base_url`, custom chat model, and custom embedding model
- fixed graph query embedding-dimension handling for non-OpenAI embedding providers
- added historical-domain prompt hardening for graph extraction
- updated visualization heuristics so historical graphs are not classified with literary-only types
- made local MinerU timeout configurable instead of failing after an unrealistically short hardcoded timeout
- made skill installation safer by restoring the previous skill if staged install fails

## Key Features

- Multi-format extraction: PDF, MD, TXT, DOCX, EPUB, MOBI, AZW3, JSON, and standalone images
- Graph-enhanced synthesis via LightRAG
- Semantic engineering for logic, entity, and structure density
- Interactive graph visualization bundled into each generated skill
- OpenAI-compatible provider support via `OPENAI_API_BASE` or `OPENAI_BASE_URL`
- Cross-lingual processing for mixed Chinese / English / other corpora
- Generated skill packaging with bundled graph DB and query script

## Installation

```bash
git clone https://github.com/yuancafe/knowledge2skills.git
cd knowledge2skills
pip install lightrag-hku pdfplumber pypdf python-docx ebooklib beautifulsoup4 mobi psutil requests pillow
```

## Basic Usage

```bash
python3 scripts/knowledge2skills_pipeline.py <file1> <file2> --name <skill-name> --install
```

## Common Flags

| Flag | Description |
| :--- | :--- |
| `--graph` | Build the LightRAG knowledge graph. |
| `--semantic` | Run semantic engineering and density analysis. |
| `--viz` | Generate interactive HTML graph visualization. |
| `--dedup` | Run entity deduplication. |
| `--high-precision` | Prefer MinerU for PDF extraction. |
| `--install` | Install the generated skill to `~/.agents/skills/`. |
| `--force` | Overwrite an existing installed skill. |

## Provider Configuration

Cloud graph builds can use any OpenAI-compatible endpoint.

Relevant environment variables:

```bash
export OPENAI_API_KEY=...
export OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
export LIGHTRAG_LLM_MODEL=qwen-max
export LIGHTRAG_EMBEDDING_MODEL=text-embedding-v4
```

The same pattern works for other compatible providers as long as the endpoint and model names are valid.

## MinerU Notes

For large scanned PDFs, local MinerU runs may take a long time.

`knowledge2skills` now uses a configurable timeout:

```bash
export KNOWLEDGE2SKILLS_MINERU_TIMEOUT=1800
```

Set it to `0` to disable the timeout entirely.

## Project Structure

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

## Notes From Real-World Use

The March 21 production run surfaced two practical lessons:
- graph quality depends heavily on domain-aware prompting and provider-compatible embedding handling
- a successful graph build is not enough; installation, queryability, and visualization all need explicit verification

## License

MIT
