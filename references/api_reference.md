# knowledge2skills Script API Reference

This document provides detailed parameters and usage instructions for the scripts in the `knowledge2skills` pipeline.
## 1. `extract_content.py` — Multi-format Extraction

Extracts content from PDF, MD, TXT, DOCX, EPUB, MOBI, AZW3, or JSON. Supports multiple files.

### Arguments
- `files` (Nargs+): One or more local file paths.
- `--output`, `-o` (Optional): Path to save the extracted JSON.

---

## 2. `lightrag_graph.py` — Graph Enrichment

Uses LightRAG to build a knowledge graph from extracted text.

### Arguments
- `input_json` (Positionary): Path to JSON from `extract_pdf.py`.
- `--output`, `-o` (Optional): Path to save graph summary.
- `--dir`, `-d` (Optional): LightRAG storage directory.

### Integration
Used to extract non-linear relationships and systemic logic, especially for high-freedom domains like Complex Science.

---

## 3. `generate_skill.py` — Skill Production

Converts extracted JSON into a complete skill package.

### Arguments
- `extracted_json` (Positionary): Path to the JSON file from `extract_pdf.py`.
- `--name`, `-n` (Required): Skill name (hyphen-case, e.g., `financial-manual`).
- `--output`, `-o` (Required): Directory where the skill folder will be created.

### Features
- **Auto-domain Detection**: Checks keywords to set `freedom_level`.
- **Reference Segmentation**: Splits content into `references/ref_XX.md` (<15k chars).
- **Workflow Detection**: Identifies numbered steps and conditional logic.

---

## 3. `install_skill.py` — Local Registration

Installs a generated skill directory into the global skill path.

### Arguments
- `skill_path` (Positionary): Path to the generated skill folder.
- `--force`, `-f` (Optional): Overwrite existing skill if it exists.

### Defaults
- Target directory: `~/.agents/skills/`

---

## 4. `knowledge2skills_pipeline.py` — Orchestrator

Wraps the entire workflow into a single command.

### Arguments
- `pdf_path` (Positionary): Path to the source PDF.
- `--name`, `-n` (Required): Name for the skill.
- `--output`, `-o` (Optional): Intermediate work directory.
- `--install`, `-i` (Optional): Automatically run the installation step.
- `--force`, `-f` (Optional): Force overwrite during installation.

### Usage Example
```bash
python3 scripts/knowledge2skills_pipeline.py book1.pdf doc2.md --name my-skill --graph --install
```
