#!/usr/bin/env python3
"""
Domain Detection and Entity Type Generator
Automatically detect document domain and generate appropriate entity types
"""

import os
import json
import asyncio
from typing import Dict, List

# Pre-defined entity type templates for common domains
DOMAIN_TEMPLATES = {
    "literature": [
        "Character", "Location", "Event", "Concept",
        "Literary_Work", "Symbol", "Creature", "Organization",
        "Time_Period", "Narrative_Element"
    ],
    "medicine": [
        "Disease", "Symptom", "Treatment", "Drug", "Anatomy",
        "Procedure", "Test", "Pathogen", "Gene", "Biomarker",
        "Patient_Group", "Outcome"
    ],
    "law": [
        "Case", "Court", "Judge", "Party", "Law",
        "Legal_Concept", "Statute", "Precedent", "Legal_Action",
        "Jurisdiction", "Legal_Document"
    ],
    "business": [
        "Company", "Product", "Person", "Technology", "Market",
        "Strategy", "Metric", "Event", "Location", "Financial_Instrument"
    ],
    "science": [
        "Theory", "Experiment", "Researcher", "Institution",
        "Method", "Data", "Finding", "Hypothesis", "Variable",
        "Equipment", "Publication"
    ],
    "history": [
        "Person", "Event", "Location", "Organization", "Time_Period",
        "Artifact", "Document", "Concept", "War", "Treaty"
    ],
    "technology": [
        "Technology", "Product", "Company", "Person", "Concept",
        "Algorithm", "Protocol", "Standard", "Platform", "Tool"
    ]
}


async def detect_domain(
    text: str,
    llm_model: str = "meta/llama-3.1-8b-instruct",
    api_key: str = None,
    base_url: str = None
) -> Dict:
    """
    Detect document domain using LLM
    
    Args:
        text: Sample text from document
        llm_model: LLM model to use
        api_key: API key
        base_url: API base URL
    
    Returns:
        {
            "domain": "primary domain",
            "subdomain": "specific subdomain",
            "confidence": 0.95,
            "reasoning": "explanation"
        }
    """
    from openai import AsyncOpenAI
    
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    base_url = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    prompt = f"""Analyze this text and identify its primary domain/field.

Common domains:
- literature (novels, poetry, plays)
- medicine (clinical, research, healthcare)
- law (legal documents, cases, statutes)
- business (corporate, finance, management)
- science (research papers, experiments)
- history (historical documents, events)
- technology (technical docs, software)
- news (journalism, current events)
- education (textbooks, courses)
- other (specify)

Text sample (first 2000 chars):
{text[:2000]}

Provide your analysis in JSON format:
{{
  "domain": "primary domain name",
  "subdomain": "more specific subdomain if applicable",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of why you chose this domain"
}}
"""
    
    response = await client.chat.completions.create(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    
    result = json.loads(response.choices[0].message.content)
    return result


async def generate_entity_types(
    domain: str,
    text_sample: str = None,
    num_types: int = 10,
    llm_model: str = "meta/llama-3.1-8b-instruct",
    api_key: str = None,
    base_url: str = None
) -> List[str]:
    """
    Generate domain-specific entity types
    
    Args:
        domain: Domain name (e.g., "literature", "medicine")
        text_sample: Optional text sample for context
        num_types: Number of entity types to generate
        llm_model: LLM model to use
        api_key: API key
        base_url: API base URL
    
    Returns:
        List of entity type names
    """
    # Check if we have a template
    if domain.lower() in DOMAIN_TEMPLATES:
        print(f"Using template for domain: {domain}")
        return DOMAIN_TEMPLATES[domain.lower()][:num_types]
    
    # Generate custom types using LLM
    from openai import AsyncOpenAI
    
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    base_url = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    context = f"\n\nText sample:\n{text_sample[:1000]}" if text_sample else ""
    
    prompt = f"""Generate {num_types} entity types for the domain: {domain}

Entity types should be:
1. Relevant to the domain
2. Specific enough to be useful
3. Cover different aspects of the domain
4. Use clear, descriptive names (e.g., "Disease", "Treatment", not "Thing1", "Thing2")
5. Use PascalCase or Snake_Case (e.g., "Legal_Document", "PatientGroup")
{context}

Output format (JSON):
{{
  "entity_types": ["Type1", "Type2", ...],
  "reasoning": "brief explanation"
}}
"""
    
    response = await client.chat.completions.create(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.5
    )
    
    result = json.loads(response.choices[0].message.content)
    return result['entity_types']


async def auto_detect_and_generate(
    text: str,
    num_types: int = 10,
    llm_model: str = "meta/llama-3.1-8b-instruct",
    api_key: str = None,
    base_url: str = None
) -> Dict:
    """
    Auto-detect domain and generate entity types in one step
    
    Returns:
        {
            "domain": "detected domain",
            "subdomain": "subdomain",
            "entity_types": ["Type1", "Type2", ...],
            "confidence": 0.95
        }
    """
    # Step 1: Detect domain
    print("Detecting domain...")
    domain_info = await detect_domain(text, llm_model, api_key, base_url)
    print(f"✓ Detected: {domain_info['domain']} (confidence: {domain_info['confidence']})")
    
    # Step 2: Generate entity types
    print(f"Generating {num_types} entity types...")
    entity_types = await generate_entity_types(
        domain=domain_info['domain'],
        text_sample=text,
        num_types=num_types,
        llm_model=llm_model,
        api_key=api_key,
        base_url=base_url
    )
    print(f"✓ Generated {len(entity_types)} types")
    
    return {
        "domain": domain_info['domain'],
        "subdomain": domain_info.get('subdomain'),
        "entity_types": entity_types,
        "confidence": domain_info['confidence'],
        "reasoning": domain_info.get('reasoning')
    }


def main():
    """CLI entry point"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Domain Detection and Entity Type Generator")
    parser.add_argument("file", help="Input file")
    parser.add_argument("-n", "--num-types", type=int, default=10, help="Number of entity types")
    parser.add_argument("-o", "--output", help="Output JSON file")
    parser.add_argument("--domain", help="Specify domain (skip detection)")
    
    args = parser.parse_args()
    
    # Read file
    sys.path.insert(0, os.path.expanduser("~/.stepfun/skills/lightrag-rag-builder/scripts"))
    from extract_text import extract_text_from_file
    
    text = extract_text_from_file(args.file)
    if not text:
        print(f"Error: Could not extract text from {args.file}")
        return
    
    # Run detection
    if args.domain:
        # Generate types for specified domain
        result = {
            "domain": args.domain,
            "entity_types": asyncio.run(generate_entity_types(
                domain=args.domain,
                text_sample=text,
                num_types=args.num_types
            ))
        }
    else:
        # Auto-detect
        result = asyncio.run(auto_detect_and_generate(
            text=text,
            num_types=args.num_types
        ))
    
    # Output
    print("\n" + "=" * 70)
    print("Results:")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✓ Saved to {args.output}")


if __name__ == "__main__":
    main()
