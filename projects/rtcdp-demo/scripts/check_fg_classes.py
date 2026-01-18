"""기존 Field Group의 클래스 참조 방식 확인"""
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

# Field Group 상세 조회
url = 'https://platform.adobe.io/data/foundation/schemaregistry/tenant/fieldgroups'
headers = {
    'Authorization': f'Bearer {os.getenv("ACCESS_TOKEN")}',
    'x-api-key': os.getenv('API_KEY'),
    'x-gw-ims-org-id': os.getenv('IMS_ORG'),
    'x-sandbox-name': os.getenv('SANDBOX_NAME'),
    'Accept': 'application/vnd.adobe.xed+json'  # 전체 정보 조회
}

r = requests.get(url, headers=headers)
if r.status_code == 200:
    data = r.json()
    print(f"=== 테넌트 Field Groups 분석 ({len(data.get('results', []))}개) ===\n")
    
    for fg in data.get('results', [])[:5]:  # 첫 5개만 확인
        print(f"Title: {fg.get('title')}")
        print(f"  meta:intendedToExtend: {fg.get('meta:intendedToExtend', [])}")
        print()
else:
    print(f"Error: {r.status_code}")
    print(r.text)
