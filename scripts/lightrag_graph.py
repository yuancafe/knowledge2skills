#!/usr/bin/env python3
"""
LightRAG Integration for knowledge2skills

This script uses LightRAG to convert extracted PDF text into a knowledge graph.
It extracts entities and relationships to inform the skill structure.

Requires:
    pip install lightrag-hku
    Environment variable: OPENAI_API_KEY (or configured provider)
"""

import os
import asyncio
import json
import argparse
from pathlib import Path

try:
    from lightrag import LightRAG, QueryParam
    # Standard OpenAI functions
    from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
    # Ollama support (Check if available in the installed version)
    try:
        from lightrag.llm.ollama import ollama_model_complete, ollama_embed
        OLLAMA_AVAILABLE = True
    except ImportError:
        OLLAMA_AVAILABLE = False
except ImportError:
    print("LightRAG not installed. Run: pip install lightrag-hku")

async def build_graph(text_content: str, working_dir: str, model_type: str = "openai", 
                  model_name: str = None, entity_types: list = None):
    """Build a knowledge graph from text using LightRAG."""
    working_dir = Path(working_dir).resolve()
    working_dir.mkdir(parents=True, exist_ok=True)

    # Configure Model Functions
    if model_type == "ollama":
        if not OLLAMA_AVAILABLE:
            raise ImportError("Ollama support not found in current LightRAG installation.")
        llm_func = ollama_model_complete
        embed_func = ollama_embed
        model_name = model_name or "qwen2.5:32b" 
        print(f"Using Local Model (Ollama): {model_name}")
        
        rag = LightRAG(
            working_dir=str(working_dir),
            llm_model_func=llm_func,
            llm_model_name=model_name,
            embedding_func=embed_func,
            embedding_model_name=model_name,
            addon_params={"entity_types": entity_types} if entity_types else {}
        )
    else:
        print(f"Using Cloud Model (OpenAI): {model_name or 'gpt-4o-mini'}")
        rag = LightRAG(
            working_dir=str(working_dir),
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete,
            addon_params={"entity_types": entity_types} if entity_types else {}
        )
    
    await rag.initialize_storages()
    
    # Check if already indexed
    kv_file = working_dir / "kv_store_full_text_hash.json"
    if kv_file.exists():
        print("Knowledge base already exists. Refreshing graph summary...")
    else:
        print(f"Inserting text (length: {len(text_content)})...")
        await rag.ainsert(text_content)
    
    print("Querying for knowledge structure (Multilingual Aware)...")
    structure_query = (
        "Analyze the provided text which may contain multiple languages (Chinese, English, Italian, etc.). "
        "Summarize the core entities, their cross-lingual relationships, and the primary workflows. "
        "Identify and map equivalent concepts across languages. "
        "Format the result as a single unified JSON with keys: entities, relationships, workflows."
    )
    
    result = await rag.aquery(structure_query, param=QueryParam(mode="global"))
    
    await rag.finalize_storages()
    return result

async def main():
    parser = argparse.ArgumentParser(description="Build Knowledge Graph from extracted text")
    parser.add_argument("input_json", help="JSON from extract_content.py")
    parser.add_argument("--output", "-o", help="Output path for graph summary")
    parser.add_argument("--dir", "-d", default="./lightrag_storage", help="Working directory")
    parser.add_argument("--model-type", choices=["openai", "ollama"], default="openai")
    parser.add_argument("--model-name", help="Specific model name to use")
    args = parser.parse_args()

    if not Path(args.input_json).exists():
        print(f"Error: File not found: {args.input_json}")
        return

    with open(args.input_json, 'r') as f:
        data = json.load(f)
    
    full_text = data.get("full_text", "")
    if not full_text:
        print("Error: No text found in input JSON")
        return

    result = await build_graph(full_text, args.dir)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
        print(f"Graph summary saved to {args.output}")
    else:
        print(result)

if __name__ == "__main__":
    if "OPENAI_API_KEY" not in os.environ:
        print("Warning: OPENAI_API_KEY not set. LightRAG will likely fail.")
    asyncio.run(main())
