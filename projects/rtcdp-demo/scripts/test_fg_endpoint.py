"""Field Group 엔드포인트 테스트"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# GET 요청 - Field Group 목록 조회
url_get = 'https://platform.adobe.io/data/foundation/schemaregistry/tenant/fieldgroups'
headers_get = {
    'Authorization': f'Bearer {os.getenv("ACCESS_TOKEN")}',
    'x-api-key': os.getenv('API_KEY'),
    'x-gw-ims-org-id': os.getenv('IMS_ORG'),
    'x-sandbox-name': os.getenv('SANDBOX_NAME'),
    'Accept': 'application/vnd.adobe.xed-id+json'
}

print("=== GET /tenant/fieldgroups ===")
r_get = requests.get(url_get, headers=headers_get)
print(f"Status: {r_get.status_code}")
if r_get.status_code == 200:
    data = r_get.json()
    print(f"Field Groups 개수: {len(data.get('results', []))}")
    if data.get('results'):
        print(f"첫 번째 Field Group: {data['results'][0].get('title')}")
else:
    print(f"Error: {r_get.text}")

print("\n=== POST /tenant/fieldgroups (간단한 테스트) ===")
# POST 요청 - 최소한의 Field Group 생성 시도
url_post = 'https://platform.adobe.io/data/foundation/schemaregistry/tenant/fieldgroups'
headers_post = {
    'Authorization': f'Bearer {os.getenv("ACCESS_TOKEN")}',
    'x-api-key': os.getenv('API_KEY'),
    'x-gw-ims-org-id': os.getenv('IMS_ORG'),
    'x-sandbox-name': os.getenv('SANDBOX_NAME'),
    'Content-Type': 'application/json'
}

# 매우 간단한 Field Group 정의
test_payload = {
    "title": "Test Field Group - DELETE ME",
    "description": "API 테스트용 임시 Field Group",
    "type": "object",
    "meta:intendedToExtend": ["https://ns.adobe.com/xdm/context/record"],
    "definitions": {
        "testFields": {
            "properties": {
                f"_{os.getenv('TENANT_ID')}": {
                    "type": "object",
                    "properties": {
                        "testField": {
                            "type": "string",
                            "title": "Test Field"
                        }
                    }
                }
            }
        }
    },
    "allOf": [
        {"$ref": "#/definitions/testFields"}
    ]
}

r_post = requests.post(url_post, headers=headers_post, json=test_payload)
print(f"Status: {r_post.status_code}")
print(f"Response: {r_post.text[:500]}")
