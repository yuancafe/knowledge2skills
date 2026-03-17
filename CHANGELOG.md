# Changelog - knowledge2skills

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-03-17
### Added
- **Core Engine**: Initial release of the Knowledge Production Pipeline.
- **Multi-format Support**: Unified extraction for PDF, DOCX, EPUB, MOBI, AZW3, Markdown, TXT, and JSON.
- **Batch Processing**: Ability to synthesize multiple files into a single unified AI skill package.
- **MinerU Integration**: Optional high-precision PDF parsing using MinerU (Magic-PDF) for complex layouts and formulas.
- **Graph RAG (LightRAG)**: Integrated Knowledge Graph construction to map non-linear relationships.
- **Interactive Visualization**: Self-contained web-based graph explorer bundled with each skill.
- **Smart Deduplication**: Automatic entity merging and alias management during graph construction.
- **Local-First Architecture**: Native support for **Ollama** backends to run RAG with zero API costs.
- **Cross-lingual Synthesis**: Ability to process mixed-language inputs (Chinese, English, Italian) and produce language-adaptive interactive skills.
- **Domain Adaptation**: Automatic detection of document domains (Finance, Psychology, History, etc.) with specialized extraction strategies.
- **Hardware Self-test**: Automatic checking of RAM/Disk requirements before deploying heavy models.
- **Sub-agent Optimization**: Explicit "Surgical Retrieval" instructions in generated `SKILL.md` for better LLM performance.

### Fixed
- Resolved `UnboundLocalError` in EPUB extraction.
- Fixed inconsistent directory naming across documentation and scripts.
- Optimized dependency installation prompts to be more interactive and informative.

---
**Author**: Leo Yuan Tsao ([@yuancafe](https://github.com/yuancafe))
