#!/usr/bin/env python3
"""
Test different parameter combinations
"""

import requests
import json
from auth_helper import AEPAuthHelper
import os

config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
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

tests = [
    ("No params", {}),
    ("Just limit", {'limit': 10}),
    ("Limit + start=0", {'limit': 10, 'start': 0}),
    ("Limit + start='0'", {'limit': 10, 'start': '0'}),
]

for name, params in tests:
    print(f"\nTest: {name}")
    print(f"Params: {params}")
    print("-" * 80)

    response = requests.get(
        url,
        headers=get_headers('application/vnd.adobe.xed-id+json'),
        params=params
    )

    if response.status_code == 200:
        data = response.json()
        count = len(data.get('results', []))
        print(f"✓ Found {count} results")
        if count > 0:
            print(f"  First: {data['results'][0].get('title', 'N/A')}")
        print(f"  _page: {data.get('_page', {})}")
    else:
        print(f"✗ Error: {response.status_code}")
