# Changelog - knowledge2skills

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-03-17
### Added
- **EvoMap Integration**: Preliminary support for GEP-A2A protocol. Ability to register nodes and publish skills as "Capsules" to the agent marketplace.
- **GraphRAG Deep Integration**: Bundling of LightRAG databases (`graph_db`) within skill packages for advanced relational reasoning.
- **Improved Visualization**: Standardized interactive HTML graph explorer.
- **Script Renaming**: Unified orchestrator renamed to `knowledge2skills_pipeline.py`.

### Enhanced
- **Reasoning Capabilities**: Explicit distinction between "Fact-based" (Standard) and "Relational" (Graph-enhanced) skill generation.
- **Documentation**: Professional bilingual READMEs and comprehensive API references.

### Fixed
- Resolved `UnboundLocalError` in EPUB extraction.
- Fixed inconsistent directory naming across documentation and scripts.
- Optimized dependency installation prompts to be more interactive and informative.

---
**Author**: Leo Yuan Tsao ([@yuancafe](https://github.com/yuancafe))
