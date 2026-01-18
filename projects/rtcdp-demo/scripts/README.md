# AEP Schema Builder Scripts

Adobe Experience Platform에 XDM 스키마를 생성하고 관리하는 Python 스크립트 모음입니다.

## 디렉토리 구조

```
scripts/
├── README.md                    # 이 파일
├── requirements.txt             # Python 패키지 의존성
├── aep_schema_builder.py       # 스키마 생성 메인 스크립트
└── .env                        # API 인증 정보 (gitignore)
```

## 설치 및 설정

### 1. Python 패키지 설치

```bash
cd scripts
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 Adobe Developer Console에서 발급받은 인증 정보를 입력합니다:

```bash
# .env 파일 생성
cp ../.env.example .env
```

`.env` 파일 편집:

```bash
# Adobe IMS (Identity Management System)
API_KEY=your_api_key_here
CLIENT_SECRET=your_client_secret_here
ACCESS_TOKEN=your_access_token_here
TECHNICAL_ACCOUNT_ID=your_technical_account_id@techacct.adobe.com
IMS_ORG=your_org_id@AdobeOrg

# Adobe Experience Platform 설정
SANDBOX_NAME=prod
TENANT_ID=_rtcdpDemo

# API Endpoint 설정
PLATFORM_GATEWAY=https://platform.adobe.io
IMS_ENDPOINT=https://ims-na1.adobelogin.com
```

### 3. Access Token 발급

Access Token은 24시간마다 갱신이 필요합니다. 다음 방법 중 하나로 발급:

**방법 1: OAuth Server-to-Server (권장)**
```bash
python auth_helper.py --generate-token
```

**방법 2: OAuth Device Flow (사용자 인증)**
```bash
python auth_helper.py --generate-token --method device
```

**방법 3: Adobe Developer Console UI**
- https://developer.adobe.com/console 접속
- 프로젝트 선택 → Generate access token 클릭
- 토큰 복사하여 `.env` 파일에 붙여넣기

> **참고**: JWT 인증은 2024년 1월부로 서비스가 종료되었습니다.
> OAuth Server-to-Server 또는 OAuth Device Flow를 사용하세요.

## 사용법

### 모든 스키마 생성 (권장)

```bash
python aep_schema_builder.py --create-all
```

다음 순서로 스키마와 데이터셋을 자동 생성합니다:
1. Profile Schema (고객 프로필)
2. Commerce Event Schema (주문/구매 이벤트)
3. Web Event Schema (웹 행동 이벤트)
4. Product Lookup Schema (상품 마스터)

### 특정 스키마만 생성

```bash
# Profile 스키마만 생성
python aep_schema_builder.py --create ../schemas/profile-schema.json

# Commerce Event 스키마 생성
python aep_schema_builder.py --create ../schemas/commerce-event-schema.json
```

### 스키마 목록 조회

```bash
python aep_schema_builder.py --list
```

### 데이터셋 생성 건너뛰기

스키마만 생성하고 데이터셋은 나중에 생성하려면:

```bash
python aep_schema_builder.py --create-all --no-datasets
```

### 다른 위치의 스키마 디렉토리 지정

```bash
python aep_schema_builder.py --create-all --schemas-dir /path/to/schemas
```

## 스크립트 동작 과정

### 1. 커스텀 Field Group 생성

각 스키마의 tenant 네임스페이스 필드(`_rtcdpDemo`)를 위한 Field Group을 먼저 생성합니다:

- `RTCDP Demo - Customer Profile - Custom Fields`
- `RTCDP Demo - Commerce Event - Custom Fields`
- `RTCDP Demo - Web Event - Custom Fields`
- `RTCDP Demo - Product Lookup - Custom Fields`

### 2. 스키마 생성

표준 XDM 클래스와 Field Group을 결합하여 스키마 생성:

**Profile Schema:**
- Class: `XDM Individual Profile`
- Field Groups:
  - Profile Person Details
  - Profile Personal Details
  - RTCDP Demo - Customer Profile - Custom Fields

**Commerce Event Schema:**
- Class: `XDM Experience Event`
- Field Groups:
  - Experience Event Commerce
  - RTCDP Demo - Commerce Event - Custom Fields

**Web Event Schema:**
- Class: `XDM Experience Event`
- Field Groups:
  - Experience Event Web
  - Experience Event Environment Details
  - RTCDP Demo - Web Event - Custom Fields

**Product Lookup Schema:**
- Class: `XDM Record`
- Field Groups:
  - RTCDP Demo - Product Lookup - Custom Fields

### 3. Profile 활성화

Profile 및 Event 스키마를 Real-Time Customer Profile에 활성화:
- `meta:immutableTags: ["union"]` 속성 추가

### 4. 데이터셋 생성

각 스키마에 대응하는 데이터셋 생성:
- `RTCDP Demo - Customer Profile Dataset`
- `RTCDP Demo - Commerce Event Dataset`
- `RTCDP Demo - Web Event Dataset`
- `RTCDP Demo - Product Lookup Dataset`

## Identity 설정

스크립트는 다음 Identity 네임스페이스를 사용합니다:

| Namespace | 설명 | Primary |
|-----------|------|---------|
| CustomerID | CRM 고객 ID | Yes (Profile) |
| Email | 이메일 주소 | No |
| Phone | 휴대전화 번호 | No |
| ECID | Experience Cloud ID | Yes (Web Events) |

**주의:** Identity 네임스페이스는 스키마 생성 전에 AEP UI에서 미리 생성되어 있어야 합니다.

## 에러 핸들링

### 인증 오류 (401 Unauthorized)

```
❌ 오류: HTTP 401
```

**해결:** Access Token이 만료되었습니다. 새로운 토큰을 발급받아 `.env` 파일을 업데이트하세요.

### 스키마가 이미 존재

```
⚠ 스키마가 이미 존재합니다: https://ns.adobe.com/...
  생성을 건너뜁니다.
```

**해결:** 정상입니다. 스크립트는 기존 스키마를 보호하기 위해 중복 생성을 방지합니다.

### Field Group 생성 실패

```
❌ Field Group 생성 실패: Validation error
```

**해결:**
1. JSON 스키마 구조 확인
2. Tenant 네임스페이스가 올바른지 확인 (`_rtcdpDemo`)
3. 표준 XDM 경로와 충돌하지 않는지 확인

### 네트워크 타임아웃

```
❌ Request timeout
```

**해결:**
1. 인터넷 연결 확인
2. `PLATFORM_GATEWAY` URL 확인
3. 방화벽/프록시 설정 확인

## API Rate Limiting

스크립트는 API Rate Limiting을 고려하여 각 스키마 생성 사이에 1초 대기 시간을 둡니다.

대량의 스키마를 생성할 경우:
- 한 번에 너무 많은 요청 전송 시 429 에러 발생 가능
- 에러 발생 시 잠시 후 재시도

## 로그 및 디버깅

스크립트는 상세한 실행 로그를 출력합니다:

```
=== 스키마 생성: RTCDP Demo - Customer Profile ===
파일: /path/to/profile-schema.json

--- Field Group 생성: RTCDP Demo - Customer Profile - Custom Fields ---
  ✓ Field Group 생성 완료: https://ns.adobe.com/.../fieldgroups/...

✓ 스키마 생성 완료
  - Schema ID: https://ns.adobe.com/.../schemas/...
  - Title: RTCDP Demo - Customer Profile

--- Profile 활성화: RTCDP Demo - Customer Profile ---
  ✓ Profile 활성화 완료

--- 데이터셋 생성: RTCDP Demo - Customer Profile Dataset ---
  ✓ 데이터셋 생성 완료: 64f3b2...
```

## 다음 단계

스키마 생성 후:

1. **Identity 네임스페이스 생성** (UI에서)
   - CustomerID
   - Email
   - Phone

2. **Primary Identity 필드 지정** (UI에서)
   - Profile Schema: `_rtcdpDemo.customerId`
   - Commerce Event: identityMap
   - Web Event: identityMap

3. **데이터 수집 준비**
   - Batch Ingestion: CSV 매핑
   - Streaming Ingestion: Web SDK 구현
   - Source Connectors: 연동 설정

4. **Profile 활성화 확인**
   - AEP UI → Schemas 메뉴에서 "Profile" 배지 확인

## 참고 자료

- [Schema Registry API Reference](https://www.adobe.io/apis/experienceplatform/home/api-reference.html#!acpdr/swagger-specs/schema-registry.yaml)
- [XDM Field Groups](https://experienceleague.adobe.com/docs/experience-platform/xdm/schema/composition.html)
- [Identity Namespaces](https://experienceleague.adobe.com/docs/experience-platform/identity/namespaces.html)
- [Real-Time Customer Profile](https://experienceleague.adobe.com/docs/experience-platform/profile/home.html)

## 문제 해결

문제 발생 시:
1. `.env` 파일의 인증 정보 확인
2. Sandbox 이름 확인 (기본값: `prod`)
3. API 토큰 유효성 확인 (24시간 후 만료)
4. Network 탭에서 API 응답 확인
5. AEP UI에서 스키마 수동 생성 시도하여 권한 확인
