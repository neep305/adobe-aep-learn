"""XDM Record 클래스의 정확한 $id 확인"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Global classes 조회
url = 'https://platform.adobe.io/data/foundation/schemaregistry/global/classes'
headers = {
    'Authorization': f'Bearer {os.getenv("ACCESS_TOKEN")}',
    'x-api-key': os.getenv('API_KEY'),
    'x-gw-ims-org-id': os.getenv('IMS_ORG'),
    'x-sandbox-name': os.getenv('SANDBOX_NAME'),
    'Accept': 'application/vnd.adobe.xed-id+json'
}

r = requests.get(url, headers=headers)
if r.status_code == 200:
    data = r.json()
    print(f"=== Global Classes ({len(data.get('results', []))}개) ===\n")
    
    # 모든 클래스 출력
    for cls in data.get('results', []):
        print(f"Title: {cls.get('title')}")
        print(f"  $id: {cls.get('$id')}")
        print()
else:
    print(f"Error: {r.status_code}")
    print(r.text)
