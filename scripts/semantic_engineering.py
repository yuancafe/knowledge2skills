#!/usr/bin/env python3
"""
Semantic Engineering Module for knowledge2skills

Combines logic from Onion Peeler and Semantic Density Analyzer:
1. Logic Density (Connectives, reasoning)
2. Entity Density (NER, technical terms, formulas)
3. Structural Density (Lists, tables, code)
4. Knowledge Unit (SKU) extraction planning
"""

import os
import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List

# Approximate tokens
CHARS_PER_TOKEN = 2

@dataclass
class SKU:
    """Standardized Knowledge Unit."""
    name: str
    logic_type: str  # Formula, Process, Heuristic, Decision_Tree
    content: str
    trigger: str
    context: dict
    source_ref: str

class SemanticEngineer:
    def __init__(self):
        self._spacy_model = None
        self._jieba_loaded = False

    def calculate_density(self, text: str) -> dict:
        """Calculate logic, entity, and structural density scores."""
        logic_score = self._calc_logic_density(text)
        entity_score = self._calc_entity_density(text)
        struct_score = self._calc_struct_density(text)
        
        final_score = (logic_score * 0.4) + (entity_score * 0.4) + (struct_score * 0.2)
        
        return {
            "logic": round(logic_score, 2),
            "entity": round(entity_score, 2),
            "struct": round(struct_score, 2),
            "total": round(final_score, 2),
            "target_sku_count": max(1, int(len(text) / 1500 * (final_score / 20))) if final_score > 0 else 1
        }

    def _calc_logic_density(self, text: str) -> float:
        connectives = [
            r'\bif\b', r'\bthen\b', r'\btherefore\b', r'\bthus\b', r'如果', r'那么', r'因此', r'所以',
            r'\bbecause\b', r'\bsince\b', r'由于', r'因为', r'\bhowever\b', r'\bbut\b', r'但是', r'然而',
            r'\bmust\b', r'\bshould\b', r'必须', r'应该', r'\blead to\b', r'\bresult in\b', r'导致', r'引起'
        ]
        count = sum(len(re.findall(p, text, re.I)) for p in connectives)
        return min(100, (count / (len(text)/100 + 1)) * 10)

    def _calc_entity_density(self, text: str) -> float:
        # Numbers, formulas, capitalized terms, technical quotes
        patterns = [
            r'\d+(?:\.\d+)?%?', # Numbers/Percentages
            r'\$[^$]+\$', # Inline Math
            r'\([A-Z]{2,}\)', # Abbreviations
            r'「[^」]+」|"[^"]+"', # Specialized terms
            r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*' # Proper nouns
        ]
        count = sum(len(re.findall(p, text)) for p in patterns)
        return min(100, (count / (len(text)/100 + 1)) * 8)

    def _calc_struct_density(self, text: str) -> float:
        # Tables, lists, code blocks
        patterns = [
            r'^\s*[-*+•]\s+', # Bullet points
            r'^\s*\d+[.)]\s+', # Numbered lists
            r'\|.+\|', # Table rows
            r'```[\s\S]*?```' # Code blocks
        ]
        count = sum(len(re.findall(p, text, re.M)) for p in patterns)
        return min(100, (count / (len(text)/500 + 1)) * 20)

    def plan_skus(self, sections: List[dict]) -> List[dict]:
        """Add semantic scores and target SKU counts to sections."""
        for sec in sections:
            content = sec.get("content", "")
            sec["semantic_analysis"] = self.calculate_density(content)
        return sections

if __name__ == "__main__":
    # Quick test
    engineer = SemanticEngineer()
    sample = "If the current ratio is less than 1.0, then the company may struggle to pay debts. Current Ratio = Assets / Liabilities."
    print(engineer.calculate_density(sample))
