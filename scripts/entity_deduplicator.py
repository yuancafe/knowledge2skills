#!/usr/bin/env python3
"""
Entity Deduplication Tool
Merge duplicate entities in RAG database
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
try:
    import Levenshtein
except ImportError:
    print("Installing python-Levenshtein...")
    os.system("pip install python-Levenshtein -q")
    import Levenshtein


class EntityDeduplicator:
    """Entity deduplication using multiple strategies"""
    
    def __init__(
        self,
        rag_dir: str,
        similarity_threshold: float = 0.85,
        strategy: str = "smart"
    ):
        self.rag_dir = Path(rag_dir)
        self.similarity_threshold = similarity_threshold
        self.strategy = strategy
        
    def load_entities(self) -> List[Dict]:
        """Load entities from RAG database"""
        entities_file = self.rag_dir / "vdb_entities.json"
        
        with open(entities_file) as f:
            data = json.load(f)
        
        return data.get('data', [])
    
    def find_duplicates(self, entities: List[Dict]) -> List[List[str]]:
        """Find duplicate entity groups"""
        duplicates = []
        entity_names = [e.get('entity_name', '') for e in entities]
        processed = set()
        
        for i, name1 in enumerate(entity_names):
            if not name1 or name1 in processed:
                continue
            
            group = [name1]
            
            for j, name2 in enumerate(entity_names):
                if i >= j or not name2 or name2 in processed:
                    continue
                
                if self._are_duplicates(name1, name2, entities[i], entities[j]):
                    group.append(name2)
                    processed.add(name2)
            
            if len(group) > 1:
                duplicates.append(group)
                processed.add(name1)
        
        return duplicates
    
    def _are_duplicates(
        self,
        name1: str,
        name2: str,
        entity1: Dict,
        entity2: Dict
    ) -> bool:
        """Check if two entities are duplicates"""
        
        # Strategy 1: Exact substring match
        if self._is_substring(name1, name2):
            return True
        
        # Strategy 2: High name similarity
        name_sim = self._name_similarity(name1, name2)
        if name_sim >= self.similarity_threshold:
            return True
        
        # Strategy 3: Context-based (if available)
        if self.strategy == "smart":
            desc1 = entity1.get('content', '')
            desc2 = entity2.get('content', '')
            
            if desc1 and desc2:
                # Simple keyword overlap
                words1 = set(desc1.lower().split())
                words2 = set(desc2.lower().split())
                overlap = len(words1 & words2) / max(len(words1), len(words2))
                
                if overlap > 0.5 and name_sim > 0.6:
                    return True
        
        return False
    
    def _is_substring(self, name1: str, name2: str) -> bool:
        """Check if one name is substring of another"""
        n1, n2 = name1.lower().strip(), name2.lower().strip()
        
        # Avoid matching very short names
        if min(len(n1), len(n2)) < 4:
            return False
        
        # Check if one is substring of other
        if n1 in n2 or n2 in n1:
            # Additional check: not just a common word
            if len(n1) > 6 or len(n2) > 6:
                return True
        
        return False
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity using Levenshtein distance"""
        n1, n2 = name1.lower().strip(), name2.lower().strip()
        
        distance = Levenshtein.distance(n1, n2)
        max_len = max(len(n1), len(n2))
        
        if max_len == 0:
            return 0.0
        
        return 1 - (distance / max_len)
    
    def select_primary(self, names: List[str]) -> str:
        """Select the best name from a group"""
        # Prefer longer, more complete names
        # Also prefer names with capital letters (proper nouns)
        
        def score(name):
            length_score = len(name)
            capital_score = sum(1 for c in name if c.isupper()) * 2
            return length_score + capital_score
        
        return max(names, key=score)
    
    def analyze(self) -> Dict:
        """Analyze entities and find duplicates"""
        print("=" * 70)
        print("Entity Deduplication Analysis")
        print("=" * 70)
        
        # Load entities
        print(f"\nLoading entities from: {self.rag_dir}")
        entities = self.load_entities()
        print(f"✓ Loaded {len(entities)} entities")
        
        # Find duplicates
        print(f"\nFinding duplicates (threshold={self.similarity_threshold}, strategy={self.strategy})...")
        duplicates = self.find_duplicates(entities)
        print(f"✓ Found {len(duplicates)} duplicate groups")
        
        # Analyze results
        total_duplicates = sum(len(group) - 1 for group in duplicates)
        
        results = {
            "total_entities": len(entities),
            "duplicate_groups": len(duplicates),
            "total_duplicates": total_duplicates,
            "unique_entities": len(entities) - total_duplicates,
            "groups": []
        }
        
        # Display results
        print(f"\n" + "=" * 70)
        print("Summary:")
        print("=" * 70)
        print(f"Total entities: {len(entities)}")
        print(f"Duplicate groups: {len(duplicates)}")
        print(f"Entities to merge: {total_duplicates}")
        print(f"Unique entities after merge: {results['unique_entities']}")
        
        if duplicates:
            print(f"\n" + "=" * 70)
            print("Duplicate Groups:")
            print("=" * 70)
            
            for i, group in enumerate(duplicates, 1):
                primary = self.select_primary(group)
                aliases = [n for n in group if n != primary]
                
                print(f"\n{i}. Primary: {primary}")
                print(f"   Aliases: {', '.join(aliases)}")
                
                results['groups'].append({
                    "primary": primary,
                    "aliases": aliases,
                    "count": len(group)
                })
        
        return results
    
    def merge(self, dry_run: bool = True) -> Dict:
        """Merge duplicate entities"""
        results = self.analyze()
        
        if dry_run:
            print(f"\n" + "=" * 70)
            print("DRY RUN - No changes made")
            print("=" * 70)
            print("Run with --execute to apply changes")
            return results
        
        # TODO: Implement actual merging using LightRAG API
        print(f"\n" + "=" * 70)
        print("Merging entities...")
        print("=" * 70)
        print("⚠️  Actual merging requires LightRAG API integration")
        print("For now, saving merge plan to file...")
        
        # Save merge plan
        merge_plan_file = self.rag_dir / "merge_plan.json"
        with open(merge_plan_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Merge plan saved to: {merge_plan_file}")
        
        return results


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Entity Deduplication Tool")
    parser.add_argument("rag_dir", help="RAG database directory")
    parser.add_argument("-t", "--threshold", type=float, default=0.85, help="Similarity threshold")
    parser.add_argument("-s", "--strategy", choices=["conservative", "smart", "aggressive"], 
                       default="smart", help="Merge strategy")
    parser.add_argument("--execute", action="store_true", help="Execute merge (default: dry run)")
    parser.add_argument("-o", "--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    deduplicator = EntityDeduplicator(
        rag_dir=args.rag_dir,
        similarity_threshold=args.threshold,
        strategy=args.strategy
    )
    
    results = deduplicator.merge(dry_run=not args.execute)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to: {args.output}")


if __name__ == "__main__":
    main()
