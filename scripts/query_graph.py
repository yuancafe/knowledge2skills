#!/usr/bin/env python3
"""
Graph Query Engine for knowledge2skills

Allows sub-agents to perform relational and global queries against 
the bundled LightRAG knowledge graph database.
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Try to find LightRAG
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
    # Note: For production, we'd want to handle local model functions here too
except ImportError:
    print("LightRAG not installed. Cannot query graph database.")
    sys.exit(1)

async def query_graph(query: str, working_dir: str, mode: str = "global"):
    """Perform a query against the persistent LightRAG database."""
    if not os.path.exists(working_dir):
        print(f"Error: Graph database not found at {working_dir}")
        return None

    # Re-initialize RAG using the bundled storage
    rag = LightRAG(
        working_dir=working_dir,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    
    await rag.initialize_storages()
    
    result = await rag.aquery(
        query,
        param=QueryParam(mode=mode)
    )
    
    await rag.finalize_storages()
    return result

def main():
    parser = argparse.ArgumentParser(description="Query the bundled Knowledge Graph")
    parser.add_argument("query", help="The question to ask the graph")
    parser.add_argument("--mode", choices=["local", "global", "hybrid"], default="hybrid", 
                        help="Query mode: global (holistic), local (specific), hybrid (both)")
    parser.add_argument("--db-path", help="Path to the graph_db folder")
    args = parser.parse_args()

    # Resolve DB Path
    # Default assumes it's being called from within the skill directory: ./references/graph_db
    script_dir = Path(__file__).parent
    db_path = args.db_path or str(script_dir.parent / "references" / "graph_db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)

    result = asyncio.run(query_graph(args.query, db_path, args.mode))
    if result:
        print(result)

if __name__ == "__main__":
    main()
