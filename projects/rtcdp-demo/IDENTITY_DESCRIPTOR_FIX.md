# Identity Descriptor 비표준 패턴 수정 완료

## 수정 개요

QA 재검증에서 발견된 CRITICAL 이슈 수정:
- **문제**: `product-lookup-schema.json`의 `meta:usesIdentity`가 AEP Schema Registry API 비표준 속성
- **해결**: Identity Descriptor API를 사용하는 표준 방식으로 변경

---

## 수정 사항

### 1. product-lookup-schema.json 정리

**파일**: `C:\dev\adobe\adobe-aep-learn\projects\rtcdp-demo\schemas\product-lookup-schema.json`

**제거된 속성**:
```json
// ❌ 제거됨 (비표준)
"productId": {
  "type": "string",
  "title": "Product ID",
  "description": "상품 고유 ID (Primary Key)",
  "meta:xdmType": "string",           // ← 제거
  "meta:xdmField": "_rtcdpDemo.productId",  // ← 제거
  "meta:usesIdentity": {               // ← 제거 (비표준!)
    "namespace": { "code": "ProductID" },
    "primary": true
  }
}
```

**수정 후** (표준 JSON Schema):
```json
// ✅ 표준 필드 정의만 유지
"productId": {
  "type": "string",
  "title": "Product ID",
  "description": "상품 고유 ID (Primary Key)"
}
```

**변경 이유**:
- `meta:usesIdentity`는 Adobe Schema Registry API에서 인식하지 않는 커스텀 속성
- Identity 설정은 별도의 **Identity Descriptor API**를 통해 수행해야 함

---

### 2. aep_schema_builder.py에 Identity 관리 기능 추가

**파일**: `C:\dev\adobe\adobe-aep-learn\projects\rtcdp-demo\scripts\aep_schema_builder.py`

#### 2.1 Identity Namespace API 초기화

```python
# __init__() 메서드에 추가
self.identity_api = f'{self.platform_gateway}/data/core/idnamespace'
```

#### 2.2 새로운 메서드 추가

**1) `create_identity_namespace()` - Namespace 생성**

```python
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
```

**API 엔드포인트**: `POST /data/core/idnamespace/identities`

**페이로드 예시**:
```json
{
  "code": "ProductID",
  "name": "Product ID",
  "idType": "NON_PEOPLE",
  "description": "Product ID for lookup schema"
}
```

**2) `_get_identity_namespace()` - Namespace 조회**

```python
def _get_identity_namespace(self, namespace_code: str) -> Optional[Dict]:
    """Namespace 코드로 Identity Namespace 검색"""
```

**기능**: 중복 생성 방지를 위해 기존 Namespace 확인

---

**3) `create_identity_descriptor()` - Identity Descriptor 생성**

```python
def create_identity_descriptor(self, schema_id: str, field_path: str,
                               namespace_code: str, is_primary: bool = True) -> Tuple[bool, Optional[Dict]]:
    """Identity Descriptor 생성

    Args:
        schema_id: 스키마 $id (예: "https://ns.adobe.com/{TENANT_ID}/schemas/...")
        field_path: Identity 필드 경로 (예: "/_rtcdpDemo/productId")
        namespace_code: Identity Namespace 코드
        is_primary: Primary Identity 여부
    """
```

**API 엔드포인트**: `POST /data/foundation/schemaregistry/tenant/descriptors`

**페이로드 예시**:
```json
{
  "@type": "xdm:descriptorIdentity",
  "xdm:sourceSchema": "https://ns.adobe.com/{TENANT_ID}/schemas/{SCHEMA_ID}",
  "xdm:sourceVersion": 1,
  "xdm:sourceProperty": "/_rtcdpDemo/productId",
  "xdm:namespace": "ProductID",
  "xdm:isPrimary": true
}
```

---

**4) `setup_lookup_identity()` - Lookup 스키마용 통합 설정**

```python
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
```

**실행 흐름**:
1. `create_identity_namespace()` 호출 → ProductID Namespace 생성
2. 2초 대기 (API 동기화)
3. `create_identity_descriptor()` 호출 → Identity Descriptor 생성

---

### 3. 스키마 생성 워크플로우 통합

**`create_schema()` 메서드 수정**:

```python
if success:
    schema_id = result.get('$id')
    print(f"✓ 스키마 생성 완료")
    print(f"  - Schema ID: {schema_id}")
    print(f"  - Title: {result.get('title')}")

    # Profile 활성화 (Profile 클래스인 경우)
    if 'profile' in schema_def.get('meta:class', '').lower():
        time.sleep(2)  # API 동기화 대기
        self._enable_for_profile(schema_id, title)

    # ✅ NEW: Lookup 스키마 Identity 설정 자동화
    meta_class = schema_def.get('meta:class', '')
    if 'record' in meta_class.lower() and 'lookup' in title.lower():
        time.sleep(2)  # API 동기화 대기
        self.setup_lookup_identity(schema_id, title)

    return True, result
```

**자동 감지 조건**:
- `meta:class`에 "record" 포함 AND
- `title`에 "lookup" 포함
- → `setup_lookup_identity()` 자동 실행

---

## 실행 흐름

### Before (비표준 방식)
```
1. product-lookup-schema.json에 meta:usesIdentity 포함
2. 스키마 생성 API 호출
3. ❌ API가 meta:usesIdentity를 무시하거나 에러 발생
4. Identity 설정 실패
```

### After (표준 방식)
```
1. product-lookup-schema.json에 표준 필드 정의만 포함
2. 스키마 생성 API 호출 → ✅ 성공
3. "lookup" 감지 → setup_lookup_identity() 자동 호출
   3-1. Identity Namespace "ProductID" 생성 (idType: NON_PEOPLE)
   3-2. Identity Descriptor 생성 (/_rtcdpDemo/productId → ProductID)
4. ✅ Primary Identity 설정 완료
```

---

## 검증 방법

### 1. 스키마 생성 실행
```bash
cd C:\dev\adobe\adobe-aep-learn\projects\rtcdp-demo\scripts
python aep_schema_builder.py --create ../schemas/product-lookup-schema.json
```

**예상 출력**:
```
=== 스키마 생성: RTCDP Demo - Product Lookup ===
✓ 스키마 생성 완료
  - Schema ID: https://ns.adobe.com/{TENANT_ID}/schemas/{SCHEMA_ID}
  - Title: RTCDP Demo - Product Lookup

=== Lookup Identity 설정: RTCDP Demo - Product Lookup ===

--- Identity Namespace 생성: ProductID ---
  ✓ Identity Namespace 생성 완료
    - ID: 12345
    - Code: ProductID
    - Type: NON_PEOPLE

--- Identity Descriptor 생성 ---
  Schema: https://ns.adobe.com/{TENANT_ID}/schemas/{SCHEMA_ID}
  Field: /_rtcdpDemo/productId
  Namespace: ProductID
  Primary: True
  ✓ Identity Descriptor 생성 완료
    - Descriptor ID: https://ns.adobe.com/{TENANT_ID}/descriptors/{DESC_ID}

✓ Lookup Identity 설정 완료
```

### 2. AEP UI 검증

**Schema 확인**:
1. AEP UI → Schemas → "RTCDP Demo - Product Lookup" 선택
2. Structure 탭 → `_rtcdpDemo.productId` 필드 확인
3. Identity 아이콘이 표시되어야 함 (Primary)

**Identity Namespace 확인**:
1. AEP UI → Identities → Custom Namespaces
2. "ProductID" Namespace 존재 확인
3. Type: NON_PEOPLE

**Descriptor 확인** (API):
```bash
GET https://platform.adobe.io/data/foundation/schemaregistry/tenant/descriptors
```

응답에서 다음 형태의 descriptor 확인:
```json
{
  "@type": "xdm:descriptorIdentity",
  "xdm:sourceSchema": "https://ns.adobe.com/{TENANT_ID}/schemas/{SCHEMA_ID}",
  "xdm:sourceProperty": "/_rtcdpDemo/productId",
  "xdm:namespace": "ProductID",
  "xdm:isPrimary": true
}
```

---

## 기술적 배경

### Identity Descriptor란?

Schema Registry에서 **필드와 Identity Namespace를 연결하는 메타데이터**입니다.

**스키마 자체에는 포함되지 않고, 별도의 Descriptor 객체로 관리됩니다.**

```
Schema Definition (schema.json)
  └─ Field: productId (type: string)

Identity Descriptor (별도 관리)
  └─ productId 필드를 "ProductID" Namespace에 매핑
  └─ Primary Identity로 설정
```

### Why NON_PEOPLE?

Identity Type 종류:
- **PEOPLE**: 사람 식별자 (Email, Phone, CRM ID)
- **DEVICE**: 디바이스 식별자 (ECID, IDFA)
- **COOKIE**: 쿠키 기반 식별자
- **CROSS_DEVICE**: 크로스 디바이스 식별자
- **NON_PEOPLE**: 사람이 아닌 엔티티 (Product, Location, Content)

상품 ID는 사람이 아닌 엔티티이므로 `NON_PEOPLE` 타입을 사용합니다.

---

## 추가 개선 사항

### 향후 확장 가능성

현재 하드코딩된 값들을 스키마 파일에서 읽어올 수 있도록 개선 가능:

```json
// product-lookup-schema.json에 메타데이터 추가 (선택적)
"meta:identityConfiguration": {
  "field": "_rtcdpDemo.productId",
  "namespace": {
    "code": "ProductID",
    "name": "Product ID",
    "type": "NON_PEOPLE"
  },
  "isPrimary": true
}
```

```python
# aep_schema_builder.py에서 동적으로 읽기
identity_config = schema_def.get('meta:identityConfiguration')
if identity_config:
    self.setup_lookup_identity(
        schema_id=schema_id,
        schema_title=title,
        namespace_code=identity_config['namespace']['code'],
        namespace_name=identity_config['namespace']['name'],
        field_path=identity_config['field']
    )
```

---

## 참고 문서

**Adobe Experience Platform API References**:
- [Schema Registry API - Descriptors](https://www.adobe.io/apis/experienceplatform/home/api-reference.html#/Descriptors)
- [Identity Service API - Namespaces](https://www.adobe.io/apis/experienceplatform/home/api-reference.html#/Identity-Namespace)
- [Identity Descriptor Specification](https://github.com/adobe/xdm/blob/master/docs/reference/descriptors/identity/descriptorIdentity.schema.md)

**XDM Field Descriptor 종류**:
- `xdm:descriptorIdentity`: Identity 필드 지정
- `xdm:descriptorRelationship`: 스키마 간 관계 정의
- `xdm:alternateDisplayInfo`: 필드 표시명 커스터마이징

---

## 변경 파일 목록

| 파일 | 변경 내용 | 라인 |
|------|----------|------|
| `schemas/product-lookup-schema.json` | `meta:usesIdentity`, `meta:xdmType`, `meta:xdmField` 제거 | 22-26 |
| `scripts/aep_schema_builder.py` | `identity_api` URL 추가 | 55 |
| `scripts/aep_schema_builder.py` | `create_identity_namespace()` 추가 | 371-412 |
| `scripts/aep_schema_builder.py` | `_get_identity_namespace()` 추가 | 414-418 |
| `scripts/aep_schema_builder.py` | `create_identity_descriptor()` 추가 | 420-464 |
| `scripts/aep_schema_builder.py` | `setup_lookup_identity()` 추가 | 466-502 |
| `scripts/aep_schema_builder.py` | `create_schema()`에 자동 설정 로직 추가 | 228-232 |

---

## 결론

**수정 완료 항목**:
- ✅ product-lookup-schema.json에서 비표준 속성 제거
- ✅ Identity Namespace 생성 API 구현
- ✅ Identity Descriptor 생성 API 구현
- ✅ Lookup 스키마 자동 감지 및 Identity 설정 통합
- ✅ 스키마 생성 워크플로우에 통합

**이제 표준 AEP API 패턴을 따르며, Lookup 스키마 생성 시 Identity가 자동으로 설정됩니다.**

---

**작성일**: 2026-01-18
**작성자**: AEP Developer Agent (Claude Code)
