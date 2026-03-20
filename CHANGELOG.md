# Changelog - knowledge2skills

All notable changes to this project will be documented in this file.

## [1.40] - 2026-03-21

### Fixed
- Fixed `.mobi` and `.azw3` extraction so the pipeline reads unpacked book content instead of treating the extracted path itself as content.
- Fixed pipeline domain detection to call the async detector correctly instead of instantiating the wrong API shape.
- Fixed OpenAI-compatible graph querying so embedding dimensions are loaded from the bundled graph DB rather than assuming OpenAI defaults.
- Fixed historical graph visualization classification so non-literary corpora are not forced into literary-only node types.
- Fixed installation rollback behavior so an existing installed skill can be restored if a staged overwrite fails.
- Fixed repository hygiene by adding ignore rules for `.DS_Store`, `__pycache__`, and bytecode artifacts.

### Added
- Added standalone image and map ingestion for `.png`, `.jpg`, `.jpeg`, and `.webp` sources.
- Added OpenAI-compatible provider support for LightRAG graph builds through configurable `OPENAI_API_BASE` / `OPENAI_BASE_URL`, custom chat models, and custom embedding models.
- Added historical-domain extraction guardrails and examples for better graph quality on scholarly and historical corpora.
- Added configurable local MinerU timeout via `KNOWLEDGE2SKILLS_MINERU_TIMEOUT`.
- Added bilingual documentation refresh for README and changelog.

### Changed
- Updated project docs, skill metadata, and workflow guidance for the March 21 production hardening release.

## [1.3.0] - 2026-03-20
### Added
- **Semantic Engineering Module**: New `scripts/semantic_engineering.py` for advanced knowledge density analysis.
- **SKU (Standardized Knowledge Unit) System**: Transitioned from simple text segmentation to structured knowledge decomposition.
- **Semantic Density Scoring**: Automatically identifies "mining zones" in documents based on logic, entity, and structural density.
- **Enhanced SKILL.md**: Generated skills now include semantic density highlights and a summary of extracted knowledge units.

---

## [1.2.0] - 2026-03-17
### Added
- **Graph RAG Loop Closure**: Bundles `scripts/query_graph.py` directly into generated skills to enable executable relational reasoning.
- **Relational Instruction Set**: Enhanced `SKILL.md` generator to inject "Graph-First" instructions for sub-agents.
- **Persistent Graph DB**: Full persistence and bundling of `graphml` and `json` knowledge bases within the skill package.

---

## [1.1.0] - 2026-03-17
### Added
- **EvoMap Integration**: Preliminary support for GEP-A2A protocol for skill marketplace distribution.
- **Superior Parsing (MinerU)**: Integrated support for **MinerU (Magic-PDF)** for high-precision extraction of complex layouts.
- **Interactive Visualization**: Standardized interactive HTML graph explorer.
- **Domain-Adaptive Entity Types**: Automatically detects document domains and applies optimized entity schemas.
- **Smart Deduplication**: Automatic entity merging and alias management.
- **Cross-lingual Intelligence**: Processes mixed-language inputs (Chinese, English, Italian).

---

## [1.0.0] - 2026-03-17
### Added
- **Core Engine Release**: First stable release of the Knowledge Production Pipeline (formerly `anything2skills`).
- **Multi-format Support**: Unified extraction for PDF, DOCX, EPUB, MOBI, AZW3, Markdown, TXT, and JSON.
- **Local-First Architecture**: Native support for **Ollama** backends.

---

## [0.8.0-beta] - 2026-03-15
### Added
- **Initial LightRAG Integration**: First experiment with Knowledge Graph-based retrieval.
- **Kindle Format Support**: Initial routing for `.mobi` and `.epub` files.

---

## [0.5.0-beta] - 2026-03-09
### Added
- **Multi-source Expansion**: Added support for `.docx` and `.md` files.
- **Freedom Levels**: Introduced `low/medium/high` freedom levels based on document domain.

---

## [0.1.0-beta] - 2026-03-07
### Added
- **Concept Phase**: Original `pdf2skills` project.
- **Basic Extraction**: Simple text and table extraction using `pdfplumber`.

---
**Author**: Leo Yuan Tsao ([@yuancafe](https://github.com/yuancafe))
