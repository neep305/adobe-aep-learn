"""
Adobe Experience Platform Schema Builder
XDM 스키마를 AEP Schema Registry API를 통해 생성하는 스크립트

사용법:
    python aep_schema_builder.py --create-all
    python aep_schema_builder.py --create profile-schema
    python aep_schema_builder.py --list
"""

import os
import sys
import json
import requests
import argparse
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class AEPSchemaBuilder:
    """Adobe Experience Platform Schema Builder"""

    def __init__(self):
        """API 인증 정보 및 엔드포인트 초기화"""
        self.api_key = os.getenv('API_KEY')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.access_token = os.getenv('ACCESS_TOKEN')
        self.ims_org = os.getenv('IMS_ORG')
        self.sandbox_name = os.getenv('SANDBOX_NAME', 'prod')
        self.tenant_id = os.getenv('TENANT_ID', 'acssandboxgdctwo')
        self.platform_gateway = os.getenv('PLATFORM_GATEWAY', 'https://platform.adobe.io')

        # 인증 정보 검증
        self._validate_credentials()

        # API 헤더 설정
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'x-api-key': self.api_key,
            'x-gw-ims-org-id': self.ims_org,
            'x-sandbox-name': self.sandbox_name,
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.adobe.xed-full+json; version=1'
        }

        # Schema Registry API 베이스 URL
        self.schema_api = f'{self.platform_gateway}/data/foundation/schemaregistry'

        # Identity Service API 베이스 URL
        self.identity_api = f'{self.platform_gateway}/data/core/idnamespace'

        print(f"✓ AEP Schema Builder 초기화 완료")
        print(f"  - Organization: {self.ims_org}")
        print(f"  - Sandbox: {self.sandbox_name}")
        print(f"  - Tenant: {self.tenant_id}")

    def _validate_credentials(self):
        """필수 인증 정보 확인"""
        required_vars = ['API_KEY', 'CLIENT_SECRET', 'ACCESS_TOKEN', 'IMS_ORG']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            print(f"❌ 오류: 다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
            print(f"   .env 파일을 확인하거나 환경 변수를 설정하세요.")
            sys.exit(1)

    def _make_request(self, method: str, url: str, data: Optional[Dict] = None,
                      params: Optional[Dict] = None) -> Tuple[bool, Optional[Dict]]:
        """HTTP 요청 실행 및 에러 핸들링"""
        return self._make_request_with_headers(method, url, data, params, self.headers)
    
    def _make_request_with_headers(self, method: str, url: str, data: Optional[Dict] = None,
                                    params: Optional[Dict] = None, 
                                    headers: Optional[Dict] = None) -> Tuple[bool, Optional[Dict]]:
        """커스텀 헤더로 HTTP 요청 실행"""
        if headers is None:
            headers = self.headers
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, {'error': f'Unsupported HTTP method: {method}'}

            # 응답 처리
            if response.status_code in [200, 201]:
                return True, response.json() if response.text else {}
            elif response.status_code == 404:
                return False, {'error': 'Not found', 'status_code': 404, 'url': url, 'response_text': response.text}
            else:
                error_data = response.json() if response.text else {}
                return False, {
                    'error': f'HTTP {response.status_code}',
                    'status_code': response.status_code,
                    'url': url,
                    'details': error_data
                }

        except requests.exceptions.Timeout:
            return False, {'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return False, {'error': 'Connection error'}
        except Exception as e:
            return False, {'error': str(e)}

    def list_schemas(self, class_filter: Optional[str] = None) -> List[Dict]:
        """생성된 스키마 목록 조회"""
        print(f"\n=== 스키마 목록 조회 ===")

        params = {}
        if class_filter:
            params['property'] = f'meta:class=={class_filter}'

        success, result = self._make_request('GET', f'{self.schema_api}/tenant/schemas', params=params)

        if success:
            schemas = result.get('results', [])
            print(f"✓ {len(schemas)}개의 스키마를 찾았습니다.")

            for schema in schemas:
                print(f"  - {schema.get('title')} ({schema.get('$id')})")

            return schemas
        else:
            print(f"❌ 스키마 목록 조회 실패: {result.get('error')}")
            return []

    def get_schema_by_title(self, title: str) -> Optional[Dict]:
        """제목으로 스키마 검색"""
        schemas = self.list_schemas()
        for schema in schemas:
            if schema.get('title') == title:
                return schema
        return None

    def create_field_group(self, field_group_def: Dict) -> Tuple[bool, Optional[Dict]]:
        """커스텀 Field Group 생성"""
        title = field_group_def.get('title', 'Unknown')
        print(f"\n--- Field Group 생성: {title} ---")

        # 기존 Field Group 확인
        existing_fg = self._get_field_group_by_title(title)
        if existing_fg:
            print(f"  ⚠ Field Group이 이미 존재합니다: {existing_fg.get('$id')}")
            return True, existing_fg

        # Field Group 생성용 헤더 (공식 문서: Accept 헤더 제외)
        fg_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'x-api-key': self.api_key,
            'x-gw-ims-org-id': self.ims_org,
            'x-sandbox-name': self.sandbox_name,
            'Content-Type': 'application/json'
            # Accept 헤더 의도적으로 제외 (공식 문서 기준)
        }
        
        print(f"\n[DEBUG] Field Group 생성 요청:")
        print(f"  URL: {self.schema_api}/tenant/fieldgroups")
        print(f"  Payload: {json.dumps(field_group_def, indent=2, ensure_ascii=False)}")
        
        success, result = self._make_request_with_headers(
            'POST', 
            f'{self.schema_api}/tenant/fieldgroups',
            data=field_group_def,
            headers=fg_headers
        )

        if success:
            print(f"  ✓ Field Group 생성 완료: {result.get('$id')}")
            return True, result
        else:
            print(f"  ❌ Field Group 생성 실패: {result.get('error')}")
            if result.get('details'):
                print(f"     상세: {json.dumps(result['details'], indent=2, ensure_ascii=False)}")
            return False, result

    def _get_field_group_by_title(self, title: str) -> Optional[Dict]:
        """제목으로 Field Group 검색"""
        # Field Group 목록 조회 시 Accept 헤더 필요
        fg_list_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'x-api-key': self.api_key,
            'x-gw-ims-org-id': self.ims_org,
            'x-sandbox-name': self.sandbox_name,
            'Accept': 'application/vnd.adobe.xed-id+json'
        }
        
        success, result = self._make_request_with_headers(
            'GET', 
            f'{self.schema_api}/tenant/fieldgroups',
            headers=fg_list_headers
        )

        if success:
            field_groups = result.get('results', [])
            for fg in field_groups:
                if fg.get('title') == title:
                    # Field Group 상세 정보 조회
                    fg_id = fg.get('meta:altId') or fg.get('$id').split('/')[-1]
                    detail_headers = fg_list_headers.copy()
                    detail_headers['Accept'] = 'application/vnd.adobe.xed+json'
                    
                    detail_success, detail_result = self._make_request_with_headers(
                        'GET',
                        f'{self.schema_api}/tenant/fieldgroups/{fg_id}',
                        headers=detail_headers
                    )
                    if detail_success:
                        return detail_result
                    return fg
        return None

    def create_schema(self, schema_file_path: str, skip_if_exists: bool = True) -> Tuple[bool, Optional[Dict]]:
        """스키마 JSON 파일로부터 스키마 생성"""
        # 파일 읽기
        try:
            with open(schema_file_path, 'r', encoding='utf-8') as f:
                schema_def = json.load(f)
        except FileNotFoundError:
            print(f"❌ 파일을 찾을 수 없습니다: {schema_file_path}")
            return False, None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            return False, None

        title = schema_def.get('title', 'Unknown')
        print(f"\n=== 스키마 생성: {title} ===")
        print(f"파일: {schema_file_path}")

        # 기존 스키마 확인
        existing_schema = self.get_schema_by_title(title)
        if existing_schema:
            if skip_if_exists:
                print(f"⚠ 스키마가 이미 존재합니다: {existing_schema.get('$id')}")
                print(f"  생성을 건너뜁니다. (업데이트하려면 --update 옵션 사용)")
                return True, existing_schema
            else:
                print(f"⚠ 기존 스키마를 삭제하고 재생성합니다...")
                self._delete_schema(existing_schema.get('$id'))

        # 커스텀 Field Group 먼저 생성
        custom_fields = self._extract_custom_fields(schema_def)
        fg_result = None
        if custom_fields:
            fg_success, fg_result = self._create_custom_field_group(title, custom_fields, schema_def)
            if not fg_success:
                print(f"❌ 커스텀 Field Group 생성 실패")
                return False, None

        # 스키마 생성용 페이로드 구성 (Field Group 참조)
        schema_payload = self._build_schema_payload(schema_def, fg_result)

        # 스키마 생성
        success, result = self._make_request('POST', f'{self.schema_api}/tenant/schemas',
                                             data=schema_payload)

        print(f"\n[DEBUG] API 응답:")
        print(f"  - success: {success}")
        print(f"  - result: {json.dumps(result, indent=2, ensure_ascii=False) if result else 'None'}")

        if success:
            schema_id = result.get('$id')
            print(f"✓ 스키마 생성 완료")
            print(f"  - Schema ID: {schema_id}")
            print(f"  - Title: {result.get('title')}")

            # Profile 활성화 (Profile 클래스인 경우)
            if 'profile' in schema_def.get('meta:class', '').lower():
                time.sleep(2)  # API 동기화 대기
                self._enable_for_profile(schema_id, title)

            # Lookup 스키마 Identity 설정 (Record 클래스이고 "lookup"이 제목에 포함된 경우)
            meta_class = schema_def.get('meta:class', '')
            if 'record' in meta_class.lower() and 'lookup' in title.lower():
                time.sleep(2)  # API 동기화 대기
                self.setup_lookup_identity(schema_id, title)

            return True, result
        else:
            print(f"❌ 스키마 생성 실패: {result.get('error')}")
            if result.get('details'):
                print(f"   상세: {json.dumps(result['details'], indent=2, ensure_ascii=False)}")
            return False, result

    def _extract_custom_fields(self, schema_def: Dict) -> Optional[Dict]:
        """스키마 정의에서 커스텀 필드(tenant 네임스페이스) 추출"""
        # allOf의 마지막 항목에서 커스텀 필드 찾기
        all_of = schema_def.get('allOf', [])
        for item in all_of:
            if 'properties' in item:
                for key, value in item['properties'].items():
                    if key.startswith('_'):  # Tenant 네임스페이스 필드
                        return {key: value}
        return None

    def _create_custom_field_group(self, schema_title: str, custom_fields: Dict,
                                   schema_def: Dict) -> Tuple[bool, Optional[Dict]]:
        """커스텀 필드를 위한 Field Group 생성"""
        field_group_title = f"{schema_title} - Custom Fields"

        # Field Group 정의
        field_group_def = {
            "title": field_group_title,
            "description": f"{schema_title}의 커스텀 필드 그룹",
            "type": "object",
            "meta:intendedToExtend": [
                schema_def.get('meta:class')
            ],
            "definitions": {
                "customFields": {
                    "type": "object",
                    "properties": custom_fields
                }
            },
            "allOf": [
                {
                    "$ref": "#/definitions/customFields"
                }
            ]
        }

        return self.create_field_group(field_group_def)

    def _build_schema_payload(self, schema_def: Dict, custom_fg: Optional[Dict] = None) -> Dict:
        """스키마 생성 API 페이로드 구성"""
        # 기본 메타데이터
        payload = {
            "title": schema_def.get('title'),
            "description": schema_def.get('description', ''),
            "type": "object",
            "meta:class": schema_def.get('meta:class')
        }

        # allOf 배열 구성: 첫 번째 요소는 반드시 클래스 참조
        all_of = [
            {"$ref": schema_def.get('meta:class')}
        ]
        
        # 표준 Field Group 참조 추가 (behaviors 제외)
        for item in schema_def.get('allOf', []):
            if '$ref' in item:
                ref = item['$ref']
                # behaviors (record, time-series 등)와 클래스는 제외
                if (ref.startswith('https://ns.adobe.com') and 
                    '/data/' not in ref and 
                    ref != schema_def.get('meta:class')):
                    all_of.append(item)

        # 커스텀 Field Group 참조 추가
        if custom_fg:
            print(f"  ℹ 커스텀 Field Group을 스키마에 참조 추가")
            all_of.append({
                "$ref": custom_fg.get('$id')
            })

        payload['allOf'] = all_of

        return payload

    def _enable_for_profile(self, schema_id: str, schema_title: str) -> bool:
        """스키마를 Real-Time Customer Profile에 활성화"""
        print(f"\n--- Profile 활성화: {schema_title} ---")

        # PATCH 요청으로 Profile 활성화
        patch_data = [
            {
                "op": "add",
                "path": "/meta:immutableTags",
                "value": ["union"]
            }
        ]

        # Schema ID에서 tenant 경로 추출
        schema_path = schema_id.split('/')[-1]
        url = f'{self.schema_api}/tenant/schemas/{schema_path}'

        # PATCH 요청을 위한 특별한 헤더
        patch_headers = self.headers.copy()
        patch_headers['Content-Type'] = 'application/json'

        try:
            response = requests.patch(url, headers=patch_headers, json=patch_data, timeout=30)

            if response.status_code == 200:
                print(f"  ✓ Profile 활성화 완료")
                return True
            else:
                print(f"  ❌ Profile 활성화 실패: HTTP {response.status_code}")
                if response.text:
                    print(f"     {response.text}")
                return False

        except Exception as e:
            print(f"  ❌ Profile 활성화 오류: {e}")
            return False

    def _delete_schema(self, schema_id: str) -> bool:
        """스키마 삭제"""
        schema_path = schema_id.split('/')[-1]
        url = f'{self.schema_api}/tenant/schemas/{schema_path}'

        success, result = self._make_request('DELETE', url)

        if success:
            print(f"  ✓ 스키마 삭제 완료: {schema_id}")
            return True
        else:
            print(f"  ❌ 스키마 삭제 실패: {result.get('error')}")
            return False

    def create_identity_namespace(self, namespace_code: str, namespace_name: str,
                                  id_type: str = "NON_PEOPLE",
                                  description: str = "") -> Tuple[bool, Optional[Dict]]:
        """Identity Namespace 생성

        Args:
            namespace_code: Namespace 코드 (예: "ProductID")
            namespace_name: 표시 이름
            id_type: Identity 타입 ("NON_PEOPLE", "DEVICE", "COOKIE", "CROSS_DEVICE", "PEOPLE")
            description: 설명
        """
        print(f"\n--- Identity Namespace 생성: {namespace_code} ---")

        # 기존 Namespace 확인
        existing_ns = self._get_identity_namespace(namespace_code)
        if existing_ns:
            print(f"  ⚠ Identity Namespace가 이미 존재합니다: {existing_ns.get('id')}")
            return True, existing_ns

        # Namespace 정의
        namespace_def = {
            "code": namespace_code,
            "name": namespace_name,
            "idType": id_type,
            "description": description or f"{namespace_name} Identity Namespace"
        }

        # Namespace 생성
        url = f'{self.identity_api}/identities'
        success, result = self._make_request('POST', url, data=namespace_def)

        if success:
            print(f"  ✓ Identity Namespace 생성 완료")
            print(f"    - ID: {result.get('id')}")
            print(f"    - Code: {result.get('code')}")
            print(f"    - Type: {result.get('idType')}")
            return True, result
        else:
            print(f"  ❌ Identity Namespace 생성 실패: {result.get('error')}")
            if result.get('details'):
                print(f"     상세: {json.dumps(result['details'], indent=2, ensure_ascii=False)}")
            return False, result

    def _get_identity_namespace(self, namespace_code: str) -> Optional[Dict]:
        """Namespace 코드로 Identity Namespace 검색"""
        url = f'{self.identity_api}/identities'
        success, result = self._make_request('GET', url)

        if success:
            namespaces = result if isinstance(result, list) else []
            for ns in namespaces:
                if ns.get('code') == namespace_code:
                    return ns
        return None

    def create_identity_descriptor(self, schema_id: str, field_path: str,
                                   namespace_code: str, is_primary: bool = True) -> Tuple[bool, Optional[Dict]]:
        """Identity Descriptor 생성

        Args:
            schema_id: 스키마 $id (예: "https://ns.adobe.com/{TENANT_ID}/schemas/...")
            field_path: Identity 필드 경로 (예: "/_rtcdpDemo/productId")
            namespace_code: Identity Namespace 코드
            is_primary: Primary Identity 여부
        """
        print(f"\n--- Identity Descriptor 생성 ---")
        print(f"  Schema: {schema_id}")
        print(f"  Field: {field_path}")
        print(f"  Namespace: {namespace_code}")
        print(f"  Primary: {is_primary}")

        # Descriptor 정의
        descriptor_def = {
            "@type": "xdm:descriptorIdentity",
            "xdm:sourceSchema": schema_id,
            "xdm:sourceVersion": 1,
            "xdm:sourceProperty": field_path,
            "xdm:namespace": namespace_code,
            "xdm:isPrimary": is_primary
        }

        # Descriptor 생성
        url = f'{self.schema_api}/tenant/descriptors'
        success, result = self._make_request('POST', url, data=descriptor_def)

        if success:
            print(f"  ✓ Identity Descriptor 생성 완료")
            print(f"    - Descriptor ID: {result.get('@id')}")
            return True, result
        else:
            print(f"  ❌ Identity Descriptor 생성 실패: {result.get('error')}")
            if result.get('details'):
                print(f"     상세: {json.dumps(result['details'], indent=2, ensure_ascii=False)}")
            return False, result

    def setup_lookup_identity(self, schema_id: str, schema_title: str,
                             namespace_code: str = "ProductID",
                             namespace_name: str = "Product ID",
                             field_path: str = "/_rtcdpDemo/productId") -> bool:
        """Lookup 스키마용 Identity 설정 (Namespace + Descriptor)

        Args:
            schema_id: 스키마 $id
            schema_title: 스키마 제목 (로깅용)
            namespace_code: Identity Namespace 코드
            namespace_name: Namespace 표시 이름
            field_path: Primary Identity 필드 경로
        """
        print(f"\n=== Lookup Identity 설정: {schema_title} ===")

        # 1. Identity Namespace 생성
        ns_success, ns_result = self.create_identity_namespace(
            namespace_code=namespace_code,
            namespace_name=namespace_name,
            id_type="NON_PEOPLE",
            description=f"{namespace_name} for lookup schema"
        )

        if not ns_success:
            print(f"❌ Identity Namespace 생성 실패")
            return False

        # 2. Identity Descriptor 생성
        time.sleep(2)  # API 동기화 대기

        desc_success, desc_result = self.create_identity_descriptor(
            schema_id=schema_id,
            field_path=field_path,
            namespace_code=namespace_code,
            is_primary=True
        )

        if not desc_success:
            print(f"❌ Identity Descriptor 생성 실패")
            return False

        print(f"✓ Lookup Identity 설정 완료")
        return True

    def create_dataset(self, schema_id: str, dataset_name: str,
                       description: str = '') -> Tuple[bool, Optional[Dict]]:
        """스키마로부터 데이터셋 생성"""
        print(f"\n--- 데이터셋 생성: {dataset_name} ---")

        # 데이터셋 정의
        dataset_def = {
            "schemaRef": {
                "id": schema_id,
                "contentType": "application/vnd.adobe.xed-full+json;version=1"
            },
            "name": dataset_name,
            "description": description,
            "tags": {
                "rtcdp-demo": ["demo", "test"]
            }
        }

        # Catalog API 사용
        catalog_url = f'{self.platform_gateway}/data/foundation/catalog/dataSets'

        success, result = self._make_request('POST', catalog_url, data=dataset_def)

        if success:
            # 결과는 {"@/dataSets/<dataset-id>": "..."} 형태 또는 배열일 수 있음
            if isinstance(result, list) and len(result) > 0:
                dataset_id = result[0]
                print(f"  ✓ 데이터셋 생성 완료: {dataset_id}")
                return True, {'id': dataset_id}
            elif isinstance(result, dict):
                dataset_id = list(result.keys())[0].split('/')[-1]
                print(f"  ✓ 데이터셋 생성 완료: {dataset_id}")
                return True, {'id': dataset_id, **result}
            else:
                print(f"  ⚠ 예상치 못한 응답 형식: {type(result)}")
                print(f"     결과: {result}")
                return False, result
        else:
            print(f"  ❌ 데이터셋 생성 실패: {result.get('error')}")
            if result.get('details'):
                print(f"     상세: {json.dumps(result['details'], indent=2, ensure_ascii=False)}")
            return False, result

    def create_all_schemas(self, schemas_dir: str, create_datasets: bool = True):
        """schemas 디렉토리의 모든 스키마 생성"""
        print(f"\n" + "="*60)
        print(f"스키마 일괄 생성 시작")
        print(f"="*60)

        schemas_path = Path(schemas_dir)

        # 스키마 파일 찾기 (data 파일 제외)
        schema_files = [
            f for f in schemas_path.glob('*-schema.json')
            if not any(exclude in f.name for exclude in ['data.json', 'sample'])
        ]

        if not schema_files:
            print(f"❌ {schemas_dir}에서 스키마 파일을 찾을 수 없습니다.")
            return

        print(f"\n발견된 스키마 파일: {len(schema_files)}개")
        for f in schema_files:
            print(f"  - {f.name}")

        # 스키마 생성 순서 (Profile → Event → Lookup)
        ordered_files = []
        for pattern in ['profile-schema.json', 'commerce-event-schema.json',
                       'web-event-schema.json', 'product-lookup-schema.json']:
            matching = [f for f in schema_files if f.name == pattern]
            ordered_files.extend(matching)

        # 나머지 파일 추가
        remaining = [f for f in schema_files if f not in ordered_files]
        ordered_files.extend(remaining)

        # 스키마 생성
        results = []
        for schema_file in ordered_files:
            success, result = self.create_schema(str(schema_file))
            results.append({
                'file': schema_file.name,
                'success': success,
                'result': result
            })

            # 데이터셋 생성 (성공한 경우)
            if success and create_datasets and result:
                schema_id = result.get('$id')
                dataset_name = f"{result.get('title')} Dataset"
                self.create_dataset(schema_id, dataset_name, result.get('description', ''))

            time.sleep(1)  # API Rate Limiting 방지

        # 결과 요약
        print(f"\n" + "="*60)
        print(f"스키마 생성 결과 요약")
        print(f"="*60)

        success_count = sum(1 for r in results if r['success'])
        print(f"✓ 성공: {success_count}/{len(results)}")

        for r in results:
            status = "✓" if r['success'] else "❌"
            print(f"  {status} {r['file']}")

        print(f"\n완료!")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='Adobe Experience Platform Schema Builder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 모든 스키마 생성
  python aep_schema_builder.py --create-all

  # 특정 스키마만 생성
  python aep_schema_builder.py --create ../schemas/profile-schema.json

  # 스키마 목록 조회
  python aep_schema_builder.py --list

  # 데이터셋 생성 없이 스키마만 생성
  python aep_schema_builder.py --create-all --no-datasets
        """
    )

    parser.add_argument('--create-all', action='store_true',
                       help='schemas 디렉토리의 모든 스키마 생성')
    parser.add_argument('--create', type=str, metavar='FILE',
                       help='특정 스키마 파일 생성')
    parser.add_argument('--list', action='store_true',
                       help='생성된 스키마 목록 조회')
    parser.add_argument('--no-datasets', action='store_true',
                       help='데이터셋 생성 건너뛰기')
    parser.add_argument('--schemas-dir', type=str,
                       default='../schemas',
                       help='스키마 파일 디렉토리 (기본값: ../schemas)')

    args = parser.parse_args()

    # 명령어가 없으면 도움말 출력
    if not (args.create_all or args.create or args.list):
        parser.print_help()
        return

    # Schema Builder 초기화
    builder = AEPSchemaBuilder()

    # 명령 실행
    if args.list:
        builder.list_schemas()

    elif args.create_all:
        # 스크립트 위치 기준으로 schemas 디렉토리 경로 계산
        script_dir = Path(__file__).parent
        schemas_dir = (script_dir / args.schemas_dir).resolve()

        if not schemas_dir.exists():
            print(f"❌ 스키마 디렉토리를 찾을 수 없습니다: {schemas_dir}")
            return

        builder.create_all_schemas(str(schemas_dir), create_datasets=not args.no_datasets)

    elif args.create:
        schema_file = Path(args.create)
        if not schema_file.exists():
            print(f"❌ 파일을 찾을 수 없습니다: {schema_file}")
            return

        success, result = builder.create_schema(str(schema_file))

        # 데이터셋 생성
        if success and not args.no_datasets and result:
            schema_id = result.get('$id')
            dataset_name = f"{result.get('title')} Dataset"
            builder.create_dataset(schema_id, dataset_name, result.get('description', ''))


if __name__ == '__main__':
    main()
