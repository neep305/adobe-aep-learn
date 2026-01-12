#!/usr/bin/env python3
"""
Test AEPSchemaClient directly
"""

from schema_list import AEPSchemaClient
import json
import os

# Get path to config file (one level up from scripts/)
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')

client = AEPSchemaClient(config_path)

print("Testing AEPSchemaClient.list_schemas()...")
print("-" * 80)

result = client.list_schemas(limit=10, id_only=True, scope='tenant')

print(f"Response type: {type(result)}")
print(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
print(f"\nFull response:")
print(json.dumps(result, indent=2))

if 'results' in result:
    print(f"\n✓ Found {len(result['results'])} schemas")
    for idx, schema in enumerate(result['results'][:5], 1):
        print(f"  {idx}. {schema.get('title', 'Untitled')}")
else:
    print("\n✗ No 'results' key in response")
