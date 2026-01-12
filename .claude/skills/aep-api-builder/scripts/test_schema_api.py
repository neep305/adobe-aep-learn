#!/usr/bin/env python3
"""
Test script to explore Schema Registry API endpoints
"""

import requests
import json
from auth_helper import AEPAuthHelper

# Load config
config_path = 'config.json'
auth = AEPAuthHelper(config_path)

with open(config_path, 'r') as f:
    config = json.load(f)

client_id = config['client_id']
org_id = config['org_id']
sandbox = config.get('sandbox_name', 'prod')

BASE_URL = 'https://platform.adobe.io'

def get_headers(accept_type='application/json'):
    return {
        'Authorization': f'Bearer {auth.get_access_token()}',
        'x-api-key': client_id,
        'x-gw-ims-org-id': org_id,
        'x-sandbox-name': sandbox,
        'Content-Type': 'application/json',
        'Accept': accept_type
    }

# Test different endpoints
endpoints_to_test = [
    ('Tenant Schemas', f'{BASE_URL}/data/foundation/schemaregistry/tenant/schemas'),
    ('Global Schemas', f'{BASE_URL}/data/foundation/schemaregistry/global/schemas'),
    ('All Schemas (union)', f'{BASE_URL}/data/foundation/schemaregistry/schemas'),
    ('Tenant Classes', f'{BASE_URL}/data/foundation/schemaregistry/tenant/classes'),
    ('Global Classes', f'{BASE_URL}/data/foundation/schemaregistry/global/classes'),
]

print("\n" + "="*80)
print("Testing Schema Registry Endpoints")
print("="*80 + "\n")

for name, url in endpoints_to_test:
    print(f"\nTesting: {name}")
    print(f"URL: {url}")
    print("-" * 80)

    try:
        response = requests.get(
            url,
            headers=get_headers('application/vnd.adobe.xed-id+json'),
            params={'limit': 10}
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✓ Success! Found {len(results)} items")

            if results:
                print("\nFirst few items:")
                for i, item in enumerate(results[:3], 1):
                    print(f"  {i}. {item.get('title', 'Untitled')}")
                    print(f"     ID: {item.get('$id', 'N/A')}")
        else:
            print(f"✗ Error: {response.status_code}")
            try:
                error = response.json()
                print(f"  Message: {error.get('detail', error.get('message', 'Unknown error'))}")
            except:
                print(f"  Response: {response.text[:200]}")

    except Exception as e:
        print(f"✗ Exception: {e}")

print("\n" + "="*80)
