#!/usr/bin/env python3
"""
Debug script to see full API response
"""

import requests
import json
from auth_helper import AEPAuthHelper

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

url = f'{BASE_URL}/data/foundation/schemaregistry/tenant/schemas'

print("Testing tenant schemas with different accept headers...\n")

# Test with xed-id
print("1. With application/vnd.adobe.xed-id+json:")
print("-" * 80)
response = requests.get(url, headers=get_headers('application/vnd.adobe.xed-id+json'), params={'limit': 5})
print(f"Status: {response.status_code}")
data = response.json()
print(f"Response keys: {list(data.keys())}")
print(f"\nFull response:")
print(json.dumps(data, indent=2))

# Test with xed
print("\n\n2. With application/vnd.adobe.xed+json:")
print("-" * 80)
response = requests.get(url, headers=get_headers('application/vnd.adobe.xed+json'), params={'limit': 5})
print(f"Status: {response.status_code}")
data = response.json()
print(f"Response keys: {list(data.keys())}")
print(f"Number of results: {len(data.get('results', []))}")
