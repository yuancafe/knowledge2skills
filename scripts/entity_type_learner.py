#!/usr/bin/env python3
"""
Entity Type Learning and Optimization
从 LLM 提取结果中学习实体类型，动态优化类型列表
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Set
from collections import Counter


class EntityTypeLearner:
    """从 RAG 构建过程中学习和优化实体类型"""
    
    def __init__(self, skill_dir: str = None):
        self.skill_dir = Path(skill_dir or "~/.stepfun/skills/lightrag-rag-builder").expanduser()
        self.templates_file = self.skill_dir / "entity_type_templates.json"
        self.load_templates()
    
    def load_templates(self):
        """加载现有的实体类型模板"""
        if self.templates_file.exists():
            with open(self.templates_file) as f:
                self.templates = json.load(f)
        else:
            # 初始模板
            self.templates = {
                "literature": {
                    "types": [
                        "Character", "Location", "Event", "Concept",
                        "Literary_Work", "Symbol", "Creature", "Organization"
                    ],
                    "learned_types": [],
                    "usage_count": {}
                },
                "medicine": {
                    "types": [
                        "Disease", "Symptom", "Treatment", "Drug", "Anatomy",
                        "Procedure", "Test", "Pathogen", "Gene", "Biomarker"
                    ],
                    "learned_types": [],
                    "usage_count": {}
                }
            }
    
    def save_templates(self):
        """保存更新后的模板"""
        self.templates_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.templates_file, 'w') as f:
            json.dump(self.templates, f, indent=2)
    
    def extract_types_from_log(self, log_file: str) -> List[str]:
        """从 LightRAG 日志中提取 LLM 返回的实体类型"""
        extracted_types = []
        
        with open(log_file) as f:
            for line in f:
                # 查找警告信息中的实体类型
                # WARNING: Entity extraction error: invalid entity type in: ['entity', 'Divine Comedy', 'book/work', ...]
                match = re.search(r"invalid entity type in:.*?'([^']+)'.*?'([^']+)'", line)
                if match:
                    entity_type = match.group(2)
                    extracted_types.append(entity_type)
        
        return extracted_types
    
    def normalize_type_name(self, type_name: str) -> str:
        """标准化实体类型名称"""
        # 移除特殊字符，转换为 PascalCase 或 Snake_Case
        
        # 处理 "book/work" -> "Book_Work"
        if '/' in type_name:
            parts = type_name.split('/')
            normalized = '_'.join(p.capitalize() for p in parts)
            return normalized
        
        # 处理 "literary work" -> "Literary_Work"
        if ' ' in type_name:
            parts = type_name.split()
            normalized = '_'.join(p.capitalize() for p in parts)
            return normalized
        
        # 已经是标准格式
        return type_name.replace('-', '_').title()
    
    def learn_from_extraction(
        self,
        domain: str,
        extracted_types: List[str],
        min_frequency: int = 2
    ) -> Dict:
        """从提取结果中学习新的实体类型"""
        
        # 标准化类型名称
        normalized_types = [self.normalize_type_name(t) for t in extracted_types]
        
        # 统计频率
        type_counts = Counter(normalized_types)
        
        # 获取当前领域的模板
        if domain not in self.templates:
            self.templates[domain] = {
                "types": [],
                "learned_types": [],
                "usage_count": {}
            }
        
        domain_template = self.templates[domain]
        current_types = set(domain_template["types"])
        
        # 发现新类型
        new_types = []
        for type_name, count in type_counts.items():
            if count >= min_frequency and type_name not in current_types:
                new_types.append({
                    "name": type_name,
                    "frequency": count,
                    "original_forms": [t for t in extracted_types 
                                      if self.normalize_type_name(t) == type_name]
                })
        
        # 更新使用计数
        for type_name, count in type_counts.items():
            if type_name in domain_template["usage_count"]:
                domain_template["usage_count"][type_name] += count
            else:
                domain_template["usage_count"][type_name] = count
        
        return {
            "domain": domain,
            "new_types_found": len(new_types),
            "new_types": new_types,
            "total_extracted": len(extracted_types),
            "unique_types": len(type_counts)
        }
    
    def merge_learned_types(
        self,
        domain: str,
        new_types: List[Dict],
        auto_merge: bool = False
    ) -> List[str]:
        """将学习到的类型合并到模板中"""
        
        if domain not in self.templates:
            return []
        
        domain_template = self.templates[domain]
        merged = []
        
        for type_info in new_types:
            type_name = type_info["name"]
            
            if auto_merge or self._should_merge(type_info):
                if type_name not in domain_template["types"]:
                    domain_template["types"].append(type_name)
                    domain_template["learned_types"].append({
                        "name": type_name,
                        "added_at": "2026-03-17",
                        "frequency": type_info["frequency"],
                        "original_forms": type_info["original_forms"]
                    })
                    merged.append(type_name)
        
        if merged:
            self.save_templates()
        
        return merged
    
    def _should_merge(self, type_info: Dict) -> bool:
        """判断是否应该合并新类型"""
        # 频率足够高
        if type_info["frequency"] >= 5:
            return True
        
        # 名称有意义（不是单字符或数字）
        name = type_info["name"]
        if len(name) < 2 or name.isdigit():
            return False
        
        return type_info["frequency"] >= 3
    
    def get_optimized_types(
        self,
        domain: str,
        max_types: int = 15
    ) -> List[str]:
        """获取优化后的实体类型列表（按使用频率排序）"""
        
        if domain not in self.templates:
            return []
        
        domain_template = self.templates[domain]
        usage_count = domain_template["usage_count"]
        
        # 按使用频率排序
        all_types = domain_template["types"]
        sorted_types = sorted(
            all_types,
            key=lambda t: usage_count.get(t, 0),
            reverse=True
        )
        
        return sorted_types[:max_types]
    
    def analyze_rag_build(self, rag_dir: str) -> Dict:
        """分析 RAG 构建结果，提取实际使用的实体类型"""
        
        rag_path = Path(rag_dir)
        entities_file = rag_path / "vdb_entities.json"
        
        if not entities_file.exists():
            return {"error": "Entities file not found"}
        
        with open(entities_file) as f:
            data = json.load(f)
        
        entities = data.get('data', [])
        
        # 统计实际使用的类型
        actual_types = []
        for entity in entities:
            # 从 content 中提取类型信息
            content = entity.get('content', '')
            # 格式: "Entity_Name\nEntity_Name is a [type] that..."
            lines = content.split('\n')
            if len(lines) > 1:
                # 尝试从描述中推断类型
                desc = lines[1].lower()
                
                # 简单的类型推断
                if 'character' in desc or 'person' in desc:
                    actual_types.append('Character')
                elif 'location' in desc or 'place' in desc:
                    actual_types.append('Location')
                elif 'event' in desc or 'journey' in desc:
                    actual_types.append('Event')
                elif 'work' in desc or 'book' in desc or 'poem' in desc:
                    actual_types.append('Literary_Work')
                elif 'concept' in desc or 'idea' in desc:
                    actual_types.append('Concept')
                else:
                    actual_types.append('Other')
        
        type_counts = Counter(actual_types)
        
        return {
            "total_entities": len(entities),
            "type_distribution": dict(type_counts),
            "unique_types": len(type_counts)
        }


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Entity Type Learning Tool")
    parser.add_argument("command", choices=["learn", "analyze", "show", "optimize"])
    parser.add_argument("--log", help="Log file to learn from")
    parser.add_argument("--rag-dir", help="RAG directory to analyze")
    parser.add_argument("--domain", default="literature", help="Domain name")
    parser.add_argument("--auto-merge", action="store_true", help="Auto merge learned types")
    
    args = parser.parse_args()
    
    learner = EntityTypeLearner()
    
    if args.command == "learn":
        if not args.log:
            print("Error: --log required for learn command")
            return
        
        print("=" * 70)
        print("Learning Entity Types from Log")
        print("=" * 70)
        
        # 提取类型
        extracted = learner.extract_types_from_log(args.log)
        print(f"\n✓ Extracted {len(extracted)} entity type mentions")
        
        # 学习
        result = learner.learn_from_extraction(args.domain, extracted)
        
        print(f"\nLearning Results:")
        print(f"  Domain: {result['domain']}")
        print(f"  New types found: {result['new_types_found']}")
        print(f"  Total extracted: {result['total_extracted']}")
        print(f"  Unique types: {result['unique_types']}")
        
        if result['new_types']:
            print(f"\nNew Types:")
            for type_info in result['new_types']:
                print(f"  - {type_info['name']} (frequency: {type_info['frequency']})")
                print(f"    Original forms: {', '.join(set(type_info['original_forms']))}")
            
            # 合并
            merged = learner.merge_learned_types(
                args.domain,
                result['new_types'],
                auto_merge=args.auto_merge
            )
            
            if merged:
                print(f"\n✓ Merged {len(merged)} new types into template")
            else:
                print(f"\n⚠️  No types merged (use --auto-merge to force)")
    
    elif args.command == "analyze":
        if not args.rag_dir:
            print("Error: --rag-dir required for analyze command")
            return
        
        print("=" * 70)
        print("Analyzing RAG Build Results")
        print("=" * 70)
        
        result = learner.analyze_rag_build(args.rag_dir)
        
        print(f"\nAnalysis Results:")
        print(f"  Total entities: {result.get('total_entities', 0)}")
        print(f"  Unique types: {result.get('unique_types', 0)}")
        
        print(f"\nType Distribution:")
        for type_name, count in sorted(
            result.get('type_distribution', {}).items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {type_name:20s}: {count:3d}")
    
    elif args.command == "show":
        print("=" * 70)
        print(f"Entity Type Templates for: {args.domain}")
        print("=" * 70)
        
        if args.domain in learner.templates:
            template = learner.templates[args.domain]
            
            print(f"\nCurrent Types ({len(template['types'])}):")
            for i, type_name in enumerate(template['types'], 1):
                usage = template['usage_count'].get(type_name, 0)
                print(f"  {i:2d}. {type_name:20s} (used: {usage} times)")
            
            if template.get('learned_types'):
                print(f"\nLearned Types ({len(template['learned_types'])}):")
                for learned in template['learned_types']:
                    print(f"  - {learned['name']} (frequency: {learned['frequency']})")
                    print(f"    Original: {', '.join(learned['original_forms'])}")
        else:
            print(f"\n⚠️  No template found for domain: {args.domain}")
    
    elif args.command == "optimize":
        print("=" * 70)
        print(f"Optimized Entity Types for: {args.domain}")
        print("=" * 70)
        
        optimized = learner.get_optimized_types(args.domain, max_types=15)
        
        print(f"\nTop 15 Types (by usage):")
        for i, type_name in enumerate(optimized, 1):
            usage = learner.templates[args.domain]['usage_count'].get(type_name, 0)
            print(f"  {i:2d}. {type_name:20s} (used: {usage} times)")


if __name__ == "__main__":
    main()
