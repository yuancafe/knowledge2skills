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
import json
from pathlib import Path
import numpy as np
from openai import AsyncOpenAI

# Try to find LightRAG
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import openai_complete_if_cache, openai_embed
    from lightrag.utils import EmbeddingFunc
    try:
        from lightrag.llm.nvidia_openai import nvidia_openai_embed
        NVIDIA_OPENAI_AVAILABLE = True
    except ImportError:
        NVIDIA_OPENAI_AVAILABLE = False
except ImportError:
    print("LightRAG not installed. Cannot query graph database.")
    sys.exit(1)


def _get_openai_base_url() -> str | None:
    return os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")


def _is_nvidia_compatible(base_url: str | None) -> bool:
    return bool(base_url and "integrate.api.nvidia.com" in base_url)


def _load_embedding_dim(working_dir: str) -> int:
    vdb_path = Path(working_dir) / "vdb_entities.json"
    if vdb_path.exists():
        try:
            data = json.loads(vdb_path.read_text(encoding="utf-8"))
            dim = int(data.get("embedding_dim", 0))
            if dim > 0:
                return dim
        except Exception:
            pass
    return 1536


async def query_graph(query: str, working_dir: str, mode: str = "global"):
    """Perform a query against the persistent LightRAG database."""
    if not os.path.exists(working_dir):
        print(f"Error: Graph database not found at {working_dir}")
        return None

    base_url = _get_openai_base_url()
    api_key = os.environ.get("OPENAI_API_KEY")
    llm_model_name = os.environ.get("LIGHTRAG_LLM_MODEL", "gpt-4o-mini")
    embedding_model_name = os.environ.get("LIGHTRAG_EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dim = _load_embedding_dim(working_dir)

    async def llm_func(prompt, system_prompt=None, history_messages=None, **kwargs):
        return await openai_complete_if_cache(
            llm_model_name,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages or [],
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    async def embedding_func(texts: list[str]):
        if _is_nvidia_compatible(base_url) and NVIDIA_OPENAI_AVAILABLE:
            return await nvidia_openai_embed.func(
                texts,
                model=embedding_model_name,
                api_key=api_key,
                base_url=base_url,
                input_type="passage",
                trunc="END",
                encode="float",
            )
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        async with client:
            response = await client.embeddings.create(
                model=embedding_model_name,
                input=texts,
            )
        return np.array([item.embedding for item in response.data], dtype=np.float32)

    # Re-initialize RAG using the bundled storage
    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=llm_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=8192,
            model_name=embedding_model_name,
            func=embedding_func,
        ),
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
