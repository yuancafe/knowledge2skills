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
import numpy as np

try:
    from lightrag import LightRAG, QueryParam
    # Standard OpenAI functions
    from lightrag.llm.openai import (
        gpt_4o_mini_complete,
        openai_complete_if_cache,
        openai_embed,
    )
    from lightrag.utils import EmbeddingFunc
    # Ollama support (Check if available in the installed version)
    try:
        from lightrag.llm.ollama import ollama_model_complete, ollama_embed
        OLLAMA_AVAILABLE = True
    except ImportError:
        OLLAMA_AVAILABLE = False
    try:
        from lightrag.llm.nvidia_openai import nvidia_openai_embed
        NVIDIA_OPENAI_AVAILABLE = True
    except ImportError:
        NVIDIA_OPENAI_AVAILABLE = False
except ImportError:
    print("LightRAG not installed. Run: pip install lightrag-hku")

from openai import AsyncOpenAI


DEFAULT_HISTORICAL_ENTITY_TYPES = [
    "Person",
    "Place",
    "Event",
    "Organization",
    "Document",
    "Concept",
    "Period",
    "Artifact",
]


def _get_openai_base_url() -> str | None:
    return os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")


def _is_nvidia_compatible(base_url: str | None) -> bool:
    return bool(base_url and "integrate.api.nvidia.com" in base_url)


def _extract_json_body(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def _configure_historical_extraction_prompts():
    """Bias LightRAG extraction toward grounded historical-domain entities."""
    from lightrag.prompt import PROMPTS

    system_prompt = PROMPTS["entity_extraction_system_prompt"]
    if "Historical Domain Guardrails" not in system_prompt:
        guardrails = """

9. Historical Domain Guardrails:
    *   Treat the input as historical and scholarly material unless the text clearly indicates otherwise.
    *   Extract only entities and relationships that are explicitly grounded in the input text.
    *   Do not invent or import unrelated modern domains such as athletics, finance, software, consumer products, or pop culture unless the input text directly discusses them.
    *   Prefer historically meaningful names, places, wars, states, authors, texts, schools of interpretation, and source documents over generic labels.
"""
        PROMPTS["entity_extraction_system_prompt"] = system_prompt.replace(
            "---Examples---",
            guardrails + "\n---Examples---",
        )
    PROMPTS["entity_extraction_examples"] = [
        """<Entity_types>
["Person","Place","Event","Organization","Document","Concept","Period","Artifact"]

<Input Text>
```
伯里克利在战争初期主张雅典避免陆上决战，并依靠海军、城墙与帝国财政来持久作战。斯巴达则率伯罗奔尼撒同盟年年入侵阿提卡，希望通过农业破坏迫使雅典让步。
```

<Output>
entity{tuple_delimiter}伯里克利{tuple_delimiter}person{tuple_delimiter}伯里克利是雅典政治家，在战争初期主张避免陆上决战并依靠海军、城墙与财政进行持久战。 
entity{tuple_delimiter}雅典{tuple_delimiter}organization{tuple_delimiter}雅典是伯罗奔尼撒战争中的主要城邦，依靠海军、城墙和帝国财政维持战争能力。
entity{tuple_delimiter}斯巴达{tuple_delimiter}organization{tuple_delimiter}斯巴达是伯罗奔尼撒战争中的主要城邦，率领伯罗奔尼撒同盟入侵阿提卡。
entity{tuple_delimiter}伯罗奔尼撒同盟{tuple_delimiter}organization{tuple_delimiter}伯罗奔尼撒同盟是以斯巴达为主导的同盟力量，在战争中配合入侵阿提卡。
entity{tuple_delimiter}阿提卡{tuple_delimiter}place{tuple_delimiter}阿提卡是雅典周边地区，战争中屡遭斯巴达及其盟友入侵。
entity{tuple_delimiter}伯罗奔尼撒战争{tuple_delimiter}event{tuple_delimiter}伯罗奔尼撒战争是雅典与斯巴达及其盟友之间的重大希腊战争。
relation{tuple_delimiter}伯里克利{tuple_delimiter}雅典{tuple_delimiter}战略,领导{tuple_delimiter}伯里克利为雅典制定并主张依靠海军、城墙与财政的持久战略。
relation{tuple_delimiter}斯巴达{tuple_delimiter}伯罗奔尼撒同盟{tuple_delimiter}主导,联盟{tuple_delimiter}斯巴达率领伯罗奔尼撒同盟进行战争行动。
relation{tuple_delimiter}斯巴达{tuple_delimiter}阿提卡{tuple_delimiter}入侵,军事行动{tuple_delimiter}斯巴达及其盟友年年入侵阿提卡，希望迫使雅典让步。
relation{tuple_delimiter}雅典{tuple_delimiter}伯罗奔尼撒战争{tuple_delimiter}参战,核心冲突{tuple_delimiter}雅典是伯罗奔尼撒战争中的核心参战方。
relation{tuple_delimiter}斯巴达{tuple_delimiter}伯罗奔尼撒战争{tuple_delimiter}参战,核心冲突{tuple_delimiter}斯巴达是伯罗奔尼撒战争中的核心参战方。
{completion_delimiter}

""",
        """<Entity_types>
["Person","Place","Event","Organization","Document","Concept","Period","Artifact"]

<Input Text>
```
修昔底德在《伯罗奔尼撒战争史》中强调，雅典实力的增长以及斯巴达由此产生的恐惧，是战争爆发的最深层原因。
```

<Output>
entity{tuple_delimiter}修昔底德{tuple_delimiter}person{tuple_delimiter}修昔底德是《伯罗奔尼撒战争史》的作者，对战争原因提出分析。
entity{tuple_delimiter}伯罗奔尼撒战争史{tuple_delimiter}document{tuple_delimiter}《伯罗奔尼撒战争史》是修昔底德撰写的历史著作，分析战争过程与原因。
entity{tuple_delimiter}雅典{tuple_delimiter}organization{tuple_delimiter}雅典是在战争前实力持续增长的希腊城邦。
entity{tuple_delimiter}斯巴达{tuple_delimiter}organization{tuple_delimiter}斯巴达是因雅典实力增长而感到恐惧的希腊城邦。
entity{tuple_delimiter}雅典实力增长{tuple_delimiter}concept{tuple_delimiter}雅典实力增长被表述为战争爆发的深层原因之一。
entity{tuple_delimiter}斯巴达恐惧{tuple_delimiter}concept{tuple_delimiter}斯巴达对雅典实力增长的恐惧被表述为战争爆发的深层原因之一。
entity{tuple_delimiter}伯罗奔尼撒战争{tuple_delimiter}event{tuple_delimiter}伯罗奔尼撒战争是雅典与斯巴达之间爆发的重大冲突。
relation{tuple_delimiter}修昔底德{tuple_delimiter}伯罗奔尼撒战争史{tuple_delimiter}作者,著述{tuple_delimiter}修昔底德撰写了《伯罗奔尼撒战争史》。
relation{tuple_delimiter}伯罗奔尼撒战争史{tuple_delimiter}伯罗奔尼撒战争{tuple_delimiter}记述,分析{tuple_delimiter}《伯罗奔尼撒战争史》记述并分析了伯罗奔尼撒战争。
relation{tuple_delimiter}雅典实力增长{tuple_delimiter}伯罗奔尼撒战争{tuple_delimiter}成因,结构性因素{tuple_delimiter}雅典实力增长被说明为战争爆发的深层原因之一。
relation{tuple_delimiter}斯巴达恐惧{tuple_delimiter}伯罗奔尼撒战争{tuple_delimiter}成因,结构性因素{tuple_delimiter}斯巴达的恐惧被说明为战争爆发的深层原因之一。
relation{tuple_delimiter}雅典{tuple_delimiter}雅典实力增长{tuple_delimiter}属性,实力变化{tuple_delimiter}雅典是实力增长这一历史变化的承担者。
relation{tuple_delimiter}斯巴达{tuple_delimiter}斯巴达恐惧{tuple_delimiter}属性,心理动因{tuple_delimiter}斯巴达是恐惧这一历史动因的承担者。
{completion_delimiter}

""",
    ]


async def _build_nvidia_compatible_rag(
    working_dir: Path,
    llm_model_name: str,
    embedding_model_name: str,
    api_key: str,
    base_url: str,
    entity_types: list | None = None,
) -> LightRAG:
    if not NVIDIA_OPENAI_AVAILABLE:
        raise ImportError("NVIDIA OpenAI-compatible LightRAG support is unavailable.")

    async def llm_func(
        prompt,
        system_prompt=None,
        history_messages=None,
        keyword_extraction=False,
        **kwargs,
    ) -> str:
        if history_messages is None:
            history_messages = []
        result = await openai_complete_if_cache(
            llm_model_name,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )
        if keyword_extraction:
            return _extract_json_body(result)
        return result

    async def embedding_func(texts: list[str]):
        return await nvidia_openai_embed.func(
            texts,
            model=embedding_model_name,
            api_key=api_key,
            base_url=base_url,
            input_type="passage",
            trunc="END",
            encode="float",
        )

    sample_embedding = await embedding_func(["LightRAG embedding dimension probe."])
    embedding_dim = sample_embedding.shape[1]
    print(
        f"Using NVIDIA OpenAI-compatible endpoint: llm={llm_model_name}, "
        f"embedding={embedding_model_name} ({embedding_dim}d)"
    )

    return LightRAG(
        working_dir=str(working_dir),
        llm_model_func=llm_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=8192,
            model_name=embedding_model_name,
            func=embedding_func,
        ),
        addon_params={
            "entity_types": entity_types or DEFAULT_HISTORICAL_ENTITY_TYPES,
            "language": "Chinese",
        },
    )


async def _build_openai_compatible_rag(
    working_dir: Path,
    llm_model_name: str,
    embedding_model_name: str,
    api_key: str | None,
    base_url: str | None,
    entity_types: list | None = None,
) -> LightRAG:
    async def llm_func(
        prompt,
        system_prompt=None,
        history_messages=None,
        keyword_extraction=False,
        **kwargs,
    ) -> str:
        if history_messages is None:
            history_messages = []
        result = await openai_complete_if_cache(
            llm_model_name,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )
        if keyword_extraction:
            return _extract_json_body(result)
        return result

    async def embedding_func(texts: list[str]):
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        async with client:
            response = await client.embeddings.create(
                model=embedding_model_name,
                input=texts,
            )
        return np.array([item.embedding for item in response.data], dtype=np.float32)

    sample_embedding = await embedding_func(["LightRAG embedding dimension probe."])
    embedding_dim = sample_embedding.shape[1]
    print(
        f"Using OpenAI-compatible endpoint: llm={llm_model_name}, "
        f"embedding={embedding_model_name} ({embedding_dim}d)"
    )

    return LightRAG(
        working_dir=str(working_dir),
        llm_model_func=llm_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=8192,
            model_name=embedding_model_name,
            func=embedding_func,
        ),
        addon_params={
            "entity_types": entity_types or DEFAULT_HISTORICAL_ENTITY_TYPES,
            "language": "Chinese",
        },
    )

async def build_graph(text_content: str, working_dir: str, model_type: str = "openai", 
                  model_name: str = None, entity_types: list = None):
    """Build a knowledge graph from text using LightRAG."""
    working_dir = Path(working_dir).resolve()
    working_dir.mkdir(parents=True, exist_ok=True)
    entity_types = entity_types or DEFAULT_HISTORICAL_ENTITY_TYPES
    _configure_historical_extraction_prompts()

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
        base_url = _get_openai_base_url()
        api_key = os.environ.get("OPENAI_API_KEY")
        llm_model_name = model_name or os.environ.get("LIGHTRAG_LLM_MODEL") or "gpt-4o-mini"
        if _is_nvidia_compatible(base_url):
            embedding_model_name = os.environ.get(
                "LIGHTRAG_EMBEDDING_MODEL",
                "nvidia/llama-3.2-nv-embedqa-1b-v1",
            )
            rag = await _build_nvidia_compatible_rag(
                working_dir=working_dir,
                llm_model_name=llm_model_name,
                embedding_model_name=embedding_model_name,
                api_key=api_key,
                base_url=base_url,
                entity_types=entity_types,
            )
        else:
            embedding_model_name = os.environ.get(
                "LIGHTRAG_EMBEDDING_MODEL",
                "text-embedding-3-small",
            )
            rag = await _build_openai_compatible_rag(
                working_dir=working_dir,
                llm_model_name=llm_model_name,
                embedding_model_name=embedding_model_name,
                api_key=api_key,
                base_url=base_url,
                entity_types=entity_types,
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
