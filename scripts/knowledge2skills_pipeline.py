#!/usr/bin/env python3
"""
Knowledge2Skills Pipeline - Advanced Knowledge Graph Edition

Orchestrates:
  1. Multi-format extraction (with MinerU support)
  2. Domain detection & entity type learning
  3. LightRAG Knowledge Graph building (with entity deduplication)
  4. Interactive visualization generation
  5. Skill package generation & bundling
"""

import sys
import json
import argparse
import tempfile
import os
import shutil
import subprocess
from pathlib import Path

# Add scripts dir to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from extract_content import process_files, load_config, save_config
from generate_skill import generate_skill
from install_skill import install_skill, DEFAULT_TARGET
from generate_visualization import generate as generate_viz
from semantic_engineering import SemanticEngineer

def handle_evomap_publish(skill_dir: Path, skill_name: str):
    """Handle publishing the skill as an EvoMap Capsule."""
    creds_path = Path.home() / ".evomap_creds.json"
    if not creds_path.exists():
        print("\n[!] EvoMap credentials not found. Please run scripts/evomap_register.py first.")
        return False
    
    print(f"\n[EvoMap] Preparing to publish '{skill_name}' as a Capsule...")
    print(f"  - Node ID: Loaded from {creds_path.name}")
    print(f"  - Payload: {skill_dir}")
    print("  [Notice] Marketplace communication is currently in mock mode due to server timeout.")
    return True

def check_lightrag():
    """Check if lightrag is available and configured."""
    try:
        import lightrag
        return True
    except ImportError:
        return False

def detect_local_models():
    """Detect if Ollama or other local backends are running."""
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            lines = res.stdout.strip().split('\n')[1:] # Skip header
            models = [line.split()[0] for line in lines if line.strip()]
            return "ollama", models
    except:
        pass
    return None, []

def setup_lightrag():
    """Ensure LightRAG is installed and return status."""
    if check_lightrag():
        return True
    
    print("\n[!] LightRAG not found in environment.")
    ans = input("Would you like to install lightrag-hku now? (y/n): ").lower()
    if ans == 'y':
        print("Installing lightrag-hku...")
        subprocess.run([sys.executable, "-m", "pip", "install", "lightrag-hku"])
        return check_lightrag()
    return False

def run_pipeline(paths: list, skill_name: str, output_dir: str = None,
                 use_graph: bool = False, high_precision: bool = False, 
                 viz: bool = False, deduplicate: bool = False,
                 semantic: bool = False,
                 evomap: bool = False, do_install: bool = False, force: bool = False):
    
    print(f"{'='*60}")
    print(f"Knowledge2Skills Pipeline (Advanced Edition)")
    print(f"Sources: {len(paths)} files")
    print(f"Skill name: {skill_name}")
    print(f"Precision: {'High (MinerU)' if high_precision else 'Standard'}")
    print(f"Features: Graph={'ON' if use_graph else 'OFF'}, Semantic={'ON' if semantic else 'OFF'}, Viz={'ON' if viz else 'OFF'}")
    print(f"{'='*60}")

    # Step 1: Extract
    print(f"\n[1/5] Extracting content from all sources...")
    
    if output_dir:
        work_dir = Path(output_dir).resolve()
    else:
        work_dir = Path(tempfile.mkdtemp(prefix="knowledge2skills_"))
    
    work_dir.mkdir(parents=True, exist_ok=True)
    extracted = process_files(paths, high_precision=high_precision, work_dir=work_dir)
    
    # Step 2: Semantic Engineering (Optional)
    if semantic:
        print(f"\n[2/6] Performing Semantic Engineering...")
        engineer = SemanticEngineer()
        extracted["sections"] = engineer.plan_skus(extracted["sections"])
        print("  Semantic density analyzed and SKU extraction planned.")
    
    # Step 3: Graph Enrichment (Optional)
    graph_summary = None
    graph_db_dir = None
    if use_graph:
        if not setup_lightrag():
            print("\n[!] LightRAG unavailable. Skipping graph enrichment.")
        else:
            model_type, local_models = detect_local_models()
            model_name = None
            
            if model_type == "ollama" and local_models:
                print(f"\n[+] Local models detected: {', '.join(local_models)}")
                use_local = input("Use local Ollama model for RAG? (Y/n): ").lower() != 'n'
                if use_local:
                    model_name = local_models[0]
                else:
                    model_type = "openai"
            else:
                model_type = "openai"

            if model_type == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    print("\n[?] OpenAI API key not found.")
                    api_key = input("Please enter your OPENAI_API_KEY: ").strip()
                    if api_key: os.environ["OPENAI_API_KEY"] = api_key
            
            if model_type == "ollama" or os.environ.get("OPENAI_API_KEY"):
                print(f"\n[3/6] Building Knowledge Graph (Backend: {model_type})...")
                import asyncio
                from lightrag_graph import build_graph
                from domain_detector import DomainDetector
                from entity_type_learner import EntityTypeLearner
                
                graph_db_dir = work_dir / "graph_storage"
                
                # Dynamic Entity Type Selection
                try:
                    detector = DomainDetector()
                    domain_res = detector.detect_domain(extracted["full_text"][:10000])
                    domain = domain_res.get("domain", "general")
                    print(f"  Detected Graph Domain: {domain}")
                    
                    learner = EntityTypeLearner(skill_dir=str(SCRIPT_DIR.parent))
                    entity_types = learner.get_optimized_types(domain)
                    if entity_types:
                        print(f"  Using learned entity types for {domain}")
                except Exception as e:
                    print(f"  Domain/Type detection failed: {e}")
                    entity_types = None

                try:
                    graph_summary = asyncio.run(build_graph(
                        extracted["full_text"], 
                        str(graph_db_dir),
                        model_type=model_type,
                        model_name=model_name,
                        entity_types=entity_types
                    ))
                    print("  Graph built successfully.")
                    
                    # Step 4: Deduplication (Optional)
                    if deduplicate:
                        print("\n[4/6] Running entity deduplication...")
                        try:
                            from entity_deduplicator import EntityDeduplicator
                            dedup = EntityDeduplicator(str(graph_db_dir))
                            dedup.run_smart_deduplication()
                            print("  Deduplication completed.")
                        except Exception as e:
                            print(f"  Deduplication failed: {e}")
                    
                    # Step 5: Visualization (Optional)
                    if viz:
                        print("\n[5/6] Generating interactive visualization...")
                        viz_output = work_dir / "visualization"
                        generate_viz(str(graph_db_dir), str(viz_output), title=f"{skill_name} Knowledge Graph")
                        print(f"  Visualization generated in {viz_output}")
                        
                except Exception as e:
                    print(f"  Graph operations failed: {e}")
            else:
                print("  Configuration incomplete. Skipping graph.")

    # Step 6: Generate & Install
    print(f"\n[6/6] Generating skill package...")
    skill_dir = generate_skill(extracted, skill_name, str(work_dir), has_graph=use_graph)
    
    # Bundle extras
    if graph_db_dir and graph_db_dir.exists():
        target_graph = skill_dir / "references" / "graph_db"
        shutil.copytree(str(graph_db_dir), str(target_graph))
        if graph_summary:
            (skill_dir / "references" / "graph_summary.md").write_text(f"# Knowledge Graph Summary\n\n{graph_summary}")
            
    if viz and (work_dir / "visualization").exists():
        target_viz = skill_dir / "references" / "visualization"
        shutil.copytree(str(work_dir / "visualization"), str(target_viz))
        print(f"  Interactive visualization bundled into {target_viz}")

    if do_install:
        print(f"\nInstalling skill to {DEFAULT_TARGET}...")
        if install_skill(str(skill_dir), force=force):
            skill_dir = DEFAULT_TARGET / skill_dir.name
    
    # Step 7: EvoMap Publish (Optional)
    if evomap:
        handle_evomap_publish(skill_dir, skill_name)
    
    print(f"\n{'='*60}")
    print(f"Done! Advanced Pipeline completed.")
    print(f"Skill Location: {skill_dir}")
    if viz:
        print(f"Visualization: Open {skill_dir}/references/visualization/index.html in browser")
    print(f"{'='*60}")

def main():
    parser = argparse.ArgumentParser(description="Convert anything to an advanced AI skill")
    parser.add_argument("files", nargs="+", help="Files to process")
    parser.add_argument("--name", "-n", required=True, help="Skill name")
    parser.add_argument("--graph", "-g", action="store_true", help="Enable LightRAG graph enrichment")
    parser.add_argument("--semantic", "-s", action="store_true", help="Enable Semantic Engineering (density & SKU planning)")
    parser.add_argument("--high-precision", action="store_true", help="Use MinerU for PDF parsing")
    parser.add_argument("--viz", action="store_true", help="Generate interactive visualization")
    parser.add_argument("--dedup", action="store_true", help="Run entity deduplication")
    parser.add_argument("--evomap", action="store_true", help="Publish to EvoMap Marketplace")
    parser.add_argument("--install", "-i", action="store_true", help="Auto-install")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing")
    args = parser.parse_args()
    
    run_pipeline(args.files, args.name, 
                 use_graph=args.graph, 
                 high_precision=args.high_precision,
                 viz=args.viz,
                 deduplicate=args.dedup,
                 semantic=args.semantic,
                 evomap=args.evomap,
                 do_install=args.install, 
                 force=args.force)

if __name__ == "__main__":
    main()
