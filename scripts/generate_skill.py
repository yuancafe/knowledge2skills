#!/usr/bin/env python3
"""
Skill Generator for knowledge2skills

Takes extracted content (JSON from extract_content.py) and generates
a complete skill directory structure.

Usage:
    python3 generate_skill.py <extracted_json> --name <skill-name> --output <output_dir>

The generated skill follows the standard structure:
    skill-name/
    ├── SKILL.md
    ├── scripts/       (if workflows detected)
    └── references/    (segmented source material)
"""

import sys
import json
import re
import argparse
from pathlib import Path


def sanitize_skill_name(name: str) -> str:
    """Convert a string to a valid skill name (lowercase, hyphens)."""
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'-+', '-', name)
    return name.strip('-')[:40]


def title_from_name(name: str) -> str:
    """Convert skill-name to Title Case."""
    return ' '.join(w.capitalize() for w in name.split('-'))


def segment_references(sections: list, max_chars: int = 15000) -> list:
    """
    Split sections into reference file segments.
    Each segment stays under max_chars to enable dynamic context loading.
    """
    segments = []
    current_segment = {"title": "", "sections": [], "char_count": 0}

    for sec in sections:
        content = sec.get("content", "") or ""
        heading = sec.get("heading", "") or ""
        sec_len = len(content) + len(heading)

        if current_segment["char_count"] + sec_len > max_chars and current_segment["sections"]:
            segments.append(current_segment)
            current_segment = {"title": "", "sections": [], "char_count": 0}

        if not current_segment["title"] and heading:
            current_segment["title"] = heading

        current_segment["sections"].append(sec)
        current_segment["char_count"] += sec_len

    if current_segment["sections"]:
        segments.append(current_segment)

    return segments


def generate_reference_files(segments: list, refs_dir: Path) -> list:
    """Write segmented reference files and return their metadata."""
    ref_files = []
    for i, seg in enumerate(segments):
        title = seg["title"] or f"Section {i+1}"
        safe_title = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', title)[:50]
        filename = f"ref_{i+1:02d}_{safe_title}.md"

        content_lines = [f"# {title}\n"]
        for sec in seg["sections"]:
            if sec.get("heading"):
                level = sec.get("level", 2)
                prefix = "#" * min(level + 1, 4)
                content_lines.append(f"\n{prefix} {sec['heading']}\n")
            if sec.get("content"):
                content_lines.append(sec["content"])
                content_lines.append("")

        file_path = refs_dir / filename
        file_path.write_text("\n".join(content_lines), encoding="utf-8")

        ref_files.append({
            "filename": filename,
            "title": title,
            "sections": [s.get("heading", "") for s in seg["sections"] if s.get("heading")],
        })

    return ref_files


def detect_domain_and_freedom(sections: list, full_text: str) -> dict:
    """
    Analyze content to detect domain type and appropriate freedom level.
    """
    text_lower = full_text[:20000].lower()

    domain_signals = {
        "finance": ["financial", "revenue", "balance sheet", "income statement", "cash flow", "roi", "ebitda", "accounting", "财务", "报表", "利润", "会计"],
        "technology": ["api", "algorithm", "database", "framework", "deploy", "code", "function", "software", "技术", "编程", "架构", "软件"],
        "education": ["learning", "exercise", "assessment", "curriculum", "student", "pedagogy", "教学", "练习", "课程", "教育"],
        "psychology": ["behavior", "cognitive", "emotion", "therapy", "self-assessment", "mindset", "心理", "认知", "情绪", "心态"],
        "marketing": ["growth", "funnel", "conversion", "campaign", "acquisition", "branding", "增长", "营销", "转化", "品牌"],
        "management": ["strategy", "leadership", "organization", "decision", "stakeholder", "ops", "管理", "战略", "决策", "运营"],
        "communication": ["negotiation", "dialogue", "persuasion", "conflict", "presentation", "谈判", "沟通", "对话", "演说"],
        "economics": ["economy", "macroeconomics", "microeconomics", "market", "pricing", "经济", "宏观", "微观", "市场", "定价"],
        "philosophy": ["philosophy", "ethics", "epistemology", "logic", "moral", "哲学", "伦理", "认识论", "逻辑", "道德"],
        "history": ["history", "historical", "century", "dynasty", "archaeology", "历史", "世纪", "朝代", "考古"],
        "complex_science": ["complex systems", "chaos", "emergence", "network theory", "non-linear", "复杂科学", "复杂系统", "混沌", "涌现", "网络理论"],
        "career": ["recruitment", "interview", "resume", "talent", "career", "job", "求职", "招聘", "面试", "简历", "人才", "职场"],
        "study_abroad": ["admission", "university", "degree", "study abroad", "application", "留学", "申请", "大学", "学位", "录取"],
        "data_science": ["statistics", "data analysis", "machine learning", "dataset", "quantitative", "数据科学", "统计", "数据分析", "机器学习", "定量"],
        "cognitive_science": ["cognitive", "neuroscience", "brain", "perception", "mind", "认知科学", "神经科学", "大脑", "感知", "思维"],
        "environment": ["environment", "sustainability", "esg", "climate", "ecology", "环境", "可持续", "气候", "生态"]
    }

    scores = {}
    for domain, keywords in domain_signals.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[domain] = score

    if not scores:
        domain = "general"
    else:
        domain = max(scores, key=scores.get)

    freedom_map = {
        "finance": "low",
        "data_science": "low",
        "technology": "medium",
        "marketing": "medium",
        "management": "medium",
        "career": "medium",
        "study_abroad": "medium",
        "environment": "medium",
        "economics": "medium",
        "education": "high",
        "psychology": "high",
        "communication": "high",
        "philosophy": "high",
        "history": "high",
        "complex_science": "high",
        "cognitive_science": "high",
        "general": "medium",
    }

    return {
        "domain": domain,
        "freedom_level": freedom_map.get(domain, "medium"),
        "domain_scores": scores,
    }


def detect_workflows(sections: list, full_text: str) -> list:
    """
    Detect implicit workflows, step-by-step processes, and decision logic.
    """
    workflows = []
    text_lower = full_text[:30000].lower()

    # Detect numbered steps patterns
    step_patterns = [
        r'(?:step|步骤)\s*(\d+)[.:：]\s*(.+)',
        r'(\d+)\.\s+(首先|然后|接着|最后|first|then|next|finally)',
        r'(?:phase|阶段)\s*(\d+)[.:：]\s*(.+)',
    ]

    for sec in sections:
        content = sec.get("content", "") or ""
        heading = sec.get("heading", "") or ""
        steps_found = []

        for pattern in step_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                steps_found.extend(matches)

        if len(steps_found) >= 2:
            workflows.append({
                "name": heading or "Unnamed Workflow",
                "steps_count": len(steps_found),
                "source_section": heading,
            })

    # Detect decision trees / conditional logic
    decision_keywords = ["if ", "when ", "如果", "当", "otherwise", "否则", "alternatively", "或者"]
    for sec in sections:
        content = (sec.get("content", "") or "").lower()
        decision_count = sum(1 for kw in decision_keywords if kw in content)
        if decision_count >= 3:
            workflows.append({
                "name": f"Decision Logic: {sec.get('heading', 'Unnamed')}",
                "steps_count": decision_count,
                "source_section": sec.get("heading", ""),
                "type": "conditional",
            })

    return workflows


def generate_skill_md(skill_name: str, metadata: dict, domain_info: dict,
                      ref_files: list, workflows: list, sections: list, has_graph: bool = False) -> str:
    """Generate the SKILL.md content."""
    title = title_from_name(skill_name)
    book_title = metadata.get("title", "") or title
    author = metadata.get("author", "")
    total_pages = metadata.get("total_pages", 0)
    domain = domain_info["domain"]
    freedom = domain_info["freedom_level"]

    # Build description
    desc_parts = [
        f"Knowledge skill extracted from '{book_title}'",
        f"({total_pages} pages)" if total_pages else "",
        f"covering {domain} domain.",
        f"Use when tasks relate to {domain} topics covered in this book,",
        "including analysis, exercises, frameworks, and methodologies described within.",
        f"Triggers: {domain}, {book_title}, extract methodology, reference manual, {domain} analysis."
    ]
    if has_graph:
        desc_parts.append("Features integrated Graph RAG for relational reasoning.")
    
    description = " ".join(p for p in desc_parts if p)

    lines = [
        "---",
        f"name: {skill_name}",
        f"description: {description}",
        "---",
        "",
        f"# {title}",
        "",
        "## Overview",
        "",
        f"This skill encapsulates knowledge from **{book_title}**" + (f" by {author}" if author else "") + ".",
        f"Domain: **{domain.capitalize()}** | Freedom level: **{freedom}** | Source pages: **{total_pages}**",
        "",
    ]

    if has_graph:
        lines.extend([
            "## Graph RAG Features",
            "",
            "This skill is enhanced with a **Knowledge Graph Database**. It allows for high-precision relational reasoning, cause-and-effect analysis, and global thematic summaries.",
            "",
            "1. **Graph Summary**: See `references/graph_summary.md` for a high-level overview of entities and relationships.",
            "2. **Relational Queries**: Use the included query engine to answer complex 'how' and 'why' questions that span multiple chapters.",
            "",
        ])

    lines.extend([
        "## Multilingual & Interaction Guidance",
        "",
        "This skill is built from multilingual sources (which may include Chinese, English, Italian, etc.).",
        "1. **Language Adaptive**: Always respond in the language used by the user (e.g., if asked in Chinese, reply in Chinese), regardless of the source material's original language.",
        "2. **Cross-lingual Synthesis**: You are capable of summarizing concepts from foreign language sources into the user's target language.",
        "3. **Role-play Ready**: If this skill is used for an interactive game or simulation, use the extracted frameworks to maintain character/system consistency in any supported language.",
        "",
        "## Sub-agent Guidance",
        "",
        "To ensure contextual preciseness and reliability:",
    ])

    if has_graph:
        lines.append("1. **Graph-First Logic**: For complex thematic or relational questions, prioritize using `scripts/query_graph.py` to query the bundled database in `references/graph_db/`.")
        lines.append("2. **Surgical Retrieval**: Use `grep_search` on the `references/` folder to find specific sections for factual verification.")
    else:
        lines.append("1. **Surgical Retrieval**: Use `grep_search` on the `references/` folder to find relevant sections before answering. Do not rely on your general knowledge.")

    lines.extend([
        "2. **Evidence-Based**: Always cite the reference file (e.g., `ref_01_intro.md`) used for your response.",
        f"3. **Freedom Enforcement**: This is a **{freedom}** freedom skill. " + 
        ("Follow formulas and rules precisely via Python scripts." if freedom == "low" else 
         "Follow patterns but adapt to user context." if freedom == "medium" else 
         "Use frameworks as guides for open-ended exploration."),
        "",
    ])

    # Workflow section
    if workflows:
        lines.append("## Workflows")
        lines.append("")
        for i, wf in enumerate(workflows, 1):
            wf_type = wf.get("type", "sequential")
            lines.append(f"{i}. **{wf['name']}** ({wf_type}, {wf['steps_count']} steps)")
        lines.append("")
        lines.append("Refer to the relevant reference file for detailed steps.")
        lines.append("")

    # Key topics
    headings = [s["heading"] for s in sections if s.get("heading")][:20]
    if headings:
        lines.append("## Key Topics")
        lines.append("")
        for h in headings:
            lines.append(f"- {h}")
        lines.append("")

    # Reference files
    if ref_files:
        lines.append("## Reference Files")
        lines.append("")
        lines.append("Source material is segmented into reference files for dynamic context loading.")
        lines.append("Load only the relevant file based on the current task.")
        lines.append("")
        for rf in ref_files:
            section_list = ", ".join(rf["sections"][:5]) if rf["sections"] else "General content"
            lines.append(f"- **[{rf['title']}](references/{rf['filename']})**: {section_list}")
        lines.append("")

    # Usage guidance
    lines.extend([
        "## Usage",
        "",
        "1. Identify the user's task and determine which topic/chapter is relevant",
        "2. Load the corresponding reference file from `references/`",
        "3. Apply the knowledge, frameworks, or workflows from the source material",
        f"4. Maintain **{freedom}** freedom level — ",
    ])

    freedom_guidance = {
        "low": "follow extracted rules and formulas precisely, ensure deterministic accuracy",
        "medium": "follow established patterns but adapt to user context as needed",
        "high": "use frameworks as guides, encourage exploration and open-ended application",
    }
    lines[-1] += freedom_guidance.get(freedom, freedom_guidance["medium"])
    lines.append("")

    return "\n".join(lines)


def generate_skill(extracted_data: dict, skill_name: str, output_dir: str, has_graph: bool = False) -> Path:
    """
    Main generation function.
    Creates a complete skill directory from extracted knowledge data.
    """
    skill_name = sanitize_skill_name(skill_name)
    output_path = Path(output_dir).resolve()
    skill_dir = output_path / skill_name

    if skill_dir.exists():
        print(f"Warning: {skill_dir} already exists, files may be overwritten", file=sys.stderr)
    skill_dir.mkdir(parents=True, exist_ok=True)

    metadata = extracted_data.get("metadata", {})
    sections = extracted_data.get("sections", [])
    full_text = extracted_data.get("full_text", "")

    # Analyze domain and freedom level
    domain_info = detect_domain_and_freedom(sections, full_text)
    print(f"Detected domain: {domain_info['domain']} (freedom: {domain_info['freedom_level']})", file=sys.stderr)

    # Detect workflows
    workflows = detect_workflows(sections, full_text)
    print(f"Detected {len(workflows)} workflows", file=sys.stderr)

    # Segment and write reference files
    refs_dir = skill_dir / "references"
    refs_dir.mkdir(exist_ok=True)
    segments = segment_references(sections)
    ref_files = generate_reference_files(segments, refs_dir)
    print(f"Generated {len(ref_files)} reference files", file=sys.stderr)

    # Generate SKILL.md
    skill_md = generate_skill_md(skill_name, metadata, domain_info, ref_files, workflows, sections, has_graph=has_graph)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    print(f"Generated SKILL.md", file=sys.stderr)

    # Copy scripts
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    # If graph enabled, copy the query engine to the skill
    if has_graph:
        src_query_script = Path(__file__).parent / "query_graph.py"
        if src_query_script.exists():
            import shutil
            shutil.copy(str(src_query_script), str(scripts_dir / "query_graph.py"))
            print(f"Bundled Graph Query Engine to {scripts_dir / 'query_graph.py'}", file=sys.stderr)

    # Write metadata JSON
    meta_output = {
        "source_pdf": metadata,
        "domain_info": domain_info,
        "workflows": workflows,
        "reference_files": ref_files,
        "sections_count": len(sections),
        "features": {
            "graph_enhanced": has_graph
        }
    }
    (skill_dir / "skill_meta.json").write_text(
        json.dumps(meta_output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\nSkill generated at: {skill_dir}", file=sys.stderr)
    return skill_dir


def main():
    parser = argparse.ArgumentParser(description="Generate skill from extracted content")
    parser.add_argument("extracted_json", help="Path to extracted JSON (from extract_content.py)")
    parser.add_argument("--name", "-n", required=True, help="Skill name (hyphen-case)")
    parser.add_argument("--output", "-o", required=True, help="Output directory for the skill")
    args = parser.parse_args()

    json_path = Path(args.extracted_json)
    if not json_path.exists():
        print(f"Error: File not found: {args.extracted_json}", file=sys.stderr)
        sys.exit(1)

    extracted_data = json.loads(json_path.read_text(encoding="utf-8"))
    generate_skill(extracted_data, args.name, args.output)


if __name__ == "__main__":
    main()
