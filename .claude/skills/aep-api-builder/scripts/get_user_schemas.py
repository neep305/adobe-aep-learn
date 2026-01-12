#!/usr/bin/env python3
"""
Filter and display user-created schemas (excluding adhoc and system schemas)
"""

from schema_list import AEPSchemaClient
import os

config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
client = AEPSchemaClient(config_path)

result = client.list_schemas(limit=300, id_only=True, scope='tenant')

print(f"\n{'='*80}")
print(f"Current Sandbox: jason-sandbox")
print(f"{'='*80}\n")

# Filter out adhoc and system schemas
user_schemas = []
adhoc_schemas = []
system_schemas = []

for schema in result.get('results', []):
    title = schema.get('title', '')

    if 'Adhoc XDM Schema' in title or 'Adhoc schema' in title:
        adhoc_schemas.append(schema)
    elif 'qsaccel' in title or 'Random identifier' in title or 'XDM Schema for dataset' in title:
        system_schemas.append(schema)
    else:
        user_schemas.append(schema)

print(f"USER-CREATED SCHEMAS ({len(user_schemas)}):")
print(f"{'-'*80}\n")

if user_schemas:
    for idx, schema in enumerate(user_schemas, 1):
        print(f"{idx}. {schema.get('title', 'Untitled Schema')}")
        print(f"   ID: {schema.get('$id', 'N/A')}")
        print(f"   Version: {schema.get('version', 'N/A')}")
        if 'meta:class' in schema:
            print(f"   Class: {schema['meta:class']}")
        print()
else:
    print("No user-created schemas found.\n")

print(f"\n{'='*80}")
print(f"SUMMARY:")
print(f"{'-'*80}")
print(f"  User-created schemas: {len(user_schemas)}")
print(f"  System/Query schemas: {len(system_schemas)}")
print(f"  Adhoc schemas: {len(adhoc_schemas)}")
print(f"  Total: {len(result.get('results', []))}")
print(f"{'='*80}\n")
