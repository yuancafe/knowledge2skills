# Knowledge Production & Skill Generation Guide (knowledge2skills)

## Content Extraction Strategy

### What to Extract
- **Core methodology**: Frameworks, models, theories, principles
- **Workflows**: Step-by-step processes, decision trees, procedures
- **Data structures**: Tables, formulas, indicators, metrics
- **Interaction patterns**: Exercises, assessments, templates, scenarios

### What to Filter Out
- Prefaces, forewords, acknowledgments
- Case studies that are purely illustrative (unless they form the core content)
- Bibliographies and indexes
- Repetitive examples that don't add new methodology

## Domain-Specific Extraction Patterns

### Data Science / Finance (Low Freedom)
- Extract all formulas, statistical methods, and calculation rules as deterministic scripts.
- Map indicators, quantitative metrics, and dataset schemas to specific data extraction patterns.
- Preserve exact ratio definitions, significance thresholds, and mathematical logic.
- Generate rule-based analysis scripts (Python/SQL), not free-form prompts.

### Technology / Career & Recruitment / Study Abroad / Economics / Environment (Medium Freedom)
- **Technology**: Extract API patterns, architecture decisions, best practices, and code templates.
- **Career & Recruitment**: Map structured talent profiles, interview frameworks, resume parsing criteria, and recruitment funnels.
- **Study Abroad**: Extract application timelines, admission rubrics, program-specific personas, and essay templates.
- **Economics / Environment**: Extract market trend frameworks, ESG (GRI/SASB) assessment metrics, and strategic decision trees.
- General: Map troubleshooting decision trees and allow adaptation to specific business/technical contexts.

### Psychology / Philosophy / History / Complex Science / Cognitive Science / Education (High Freedom)
- **Psychology & Cognitive Science**: Extract behavioral models, self-reflection prompts, cognitive frameworks, and neuroscientific mapping.
- **Philosophy & History**: Map historical timelines, ethical frameworks, epistemological arguments, and logical structures for dialectical reasoning.
- **Complex Science**: Extract system dynamics, non-linear relationship maps, chaos/emergence models, and network theory principles.
- **Education / Communication**: Extract progression systems, curriculum designs, dialogue templates, and tactical negotiation frameworks.
- General: Allow open-ended exploration, Socratic guidance, and adaptive conceptual mapping within the extracted frameworks.

## Reference File Segmentation

### Principles
- Each reference file should be self-contained for its topic
- Keep files under 15,000 characters for efficient context loading
- Include a clear heading hierarchy for navigation
- Name files descriptively: `ref_01_chapter_title.md`

### When to Split
- Different chapters covering distinct topics → separate files
- Methodology vs. examples → separate files
- Theory vs. practical exercises → separate files

## SKILL.md Writing Guidelines

### Description (Frontmatter)
Must include:
1. What knowledge domain the skill covers
2. Source book/document title
3. Specific triggers: when should this skill be activated
4. Key capabilities: what tasks it can help with

### Body Structure
1. **Overview**: 1-2 sentences on what the skill enables
2. **Workflows**: If detected, list key processes
3. **Key Topics**: Major sections/chapters covered
4. **Reference Files**: Index with descriptions for dynamic loading
5. **Usage**: How to apply the skill with freedom level guidance

---

## Advanced Knowledge Production

### Interaction Patterns
- **Finance**: Generate or call Python scripts for mathematical analysis. Never estimate ratios manually.
- **Technology**: Provide exact command-line flags and configuration schemas.
- **Communication**: Offer "Dialogue Simulation" prompts based on extracted tactics.

### Context Efficiency (Surgical Retrieval)
To maintain high performance and low token usage:
1. **Thematic Segmentation**: Reference files should be thematic (e.g., `ref_pricing_models.md`) to allow targeted loading.
2. **Size Budgets**: Keep generated reference files under 15,000 characters. If a chapter is longer, split it into `part_1` and `part_2`.
3. **Sub-agent Indexing**: The generated `SKILL.md` must index these files with clear descriptions so the agent can use `grep_search` to find the right file without reading all of them.

---

## Graph-Based Extraction (LightRAG)

When building complex skills (Philosophy, Complex Science, System Dynamics), simple text extraction is often insufficient. **LightRAG** should be used to:

1.  **Extract Entities**: Identify key concepts, people, events, and objects.
2.  **Map Relationships**: Document how entities interact (e.g., "A causes B", "A is a subset of C").
3.  **Systemic Logic**: Identify feedback loops, emergence patterns, and dialectical arguments that are spread across multiple chapters.
4.  **Skill Enrichment**: Use the graph summary to:
    *   Inform the **Workflows** section in `SKILL.md`.
    *   Create a **Conceptual Map** reference file.
    *   Define more precise **Triggers** based on entity clusters.
