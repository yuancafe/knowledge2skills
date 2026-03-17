import requests
import json
import time
import os
from pathlib import Path

HUB_URL = "https://evomap.ai/a2a/hello"

def register_node():
    payload = {
        "protocol": "gep-a2a",
        "protocol_version": "1.0.0",
        "message_type": "hello",
        "message_id": f"msg_{int(time.time())}_init",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "payload": {
            "capabilities": {
                "knowledge_production": True,
                "multi_format_extraction": True,
                "graph_rag": True,
                "mineru_high_precision": True
            },
            "env_fingerprint": { "platform": "darwin", "arch": "arm64" }
        }
    }
    
    print(f"Sending 'hello' to {HUB_URL}...")
    try:
        response = requests.post(HUB_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("payload", {})
    except Exception as e:
        print(f"Registration failed: {e}")
        return None

if __name__ == "__main__":
    result = register_node()
    if result:
        # Save credentials locally
        config_path = Path.home() / ".evomap_creds.json"
        with open(config_path, "w") as f:
            json.dump(result, f, indent=2)
        
        print("\n" + "="*40)
        print("🎉 EvoMap Node Registered Successfully!")
        print(f"Node ID:      {result.get('your_node_id')}")
        print(f"Claim Code:   {result.get('claim_code')}")
        print(f"Claim URL:    {result.get('claim_url')}")
        print(f"Secret:       {result.get('node_secret')[:8]}...")
        print("="*40)
        print("\nCredentials saved to ~/.evomap_creds.json")
    else:
        print("Could not complete registration.")
