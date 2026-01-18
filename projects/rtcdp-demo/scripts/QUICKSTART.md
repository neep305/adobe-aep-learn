# Quick Start Guide - AEP Schema Builder

5분 안에 Adobe Experience Platform에 스키마를 생성하는 빠른 시작 가이드입니다.

## Prerequisites (사전 준비)

### 1. Adobe Experience Platform 계정 및 권한

다음 권한이 필요합니다:
- Schema Registry 읽기/쓰기 권한
- Dataset 생성 권한
- Sandbox 접근 권한

### 2. Adobe Developer Console 프로젝트

https://developer.adobe.com/console 에서:

1. **프로젝트 생성 또는 선택**
2. **Add API** → Adobe Experience Platform 선택
3. **OAuth Server-to-Server** 인증 방식 선택
4. **다음 정보 복사:**
   - Client ID (API Key)
   - Client Secret
   - Organization ID

> **참고**: JWT 인증은 2024년 1월부로 서비스가 종료되었습니다.
> 반드시 OAuth Server-to-Server를 선택하세요.

### 3. Python 환경

- Python 3.7 이상
- pip (Python 패키지 관리자)

**확인:**
```bash
python --version  # 또는 python3 --version
pip --version     # 또는 pip3 --version
```

## Step-by-Step Setup

### Step 1: 스크립트 디렉토리로 이동

```bash
cd projects/rtcdp-demo/scripts
```

### Step 2: Python 패키지 설치

```bash
pip install -r requirements.txt
```

또는 macOS/Linux:
```bash
pip3 install -r requirements.txt
```

### Step 3: 환경 변수 설정

1. `.env` 파일 생성:
```bash
# Windows
copy ..\.env.example .env

# macOS/Linux
cp ../.env.example .env
```

2. `.env` 파일 편집:
```bash
# Windows
notepad .env

# macOS/Linux
nano .env
# 또는
vi .env
```

3. **필수 값 입력:**
```bash
# Adobe Developer Console에서 복사한 정보
API_KEY=abc123...
CLIENT_SECRET=xyz789...
IMS_ORG=ABC123@AdobeOrg

# Sandbox (기본값 사용 가능)
SANDBOX_NAME=prod

# Tenant ID (기본값 사용 가능)
TENANT_ID=_rtcdpDemo

# Platform Gateway (기본값 사용)
PLATFORM_GATEWAY=https://platform.adobe.io
IMS_ENDPOINT=https://ims-na1.adobelogin.com
```

### Step 4: Access Token 생성

**방법 1: OAuth Server-to-Server (권장 - 프로덕션용)**

```bash
python auth_helper.py --generate-token
```

**방법 2: OAuth Device Flow (테스트용)**

```bash
python auth_helper.py --generate-token --method device
```

브라우저에서 표시된 URL 방문 → 코드 입력 → Adobe 계정 로그인

**토큰 검증:**
```bash
python auth_helper.py --validate-token
```

> **참고**: JWT 인증은 더 이상 지원되지 않습니다. OAuth Server-to-Server를 사용하세요.

### Step 5: 스키마 생성

**방법 1: 자동 스크립트 실행 (권장)**

Windows:
```bash
run_schema_creation.bat
```

macOS/Linux:
```bash
./run_schema_creation.sh
```

**방법 2: 수동 실행**

모든 스키마 생성:
```bash
python aep_schema_builder.py --create-all
```

특정 스키마만 생성:
```bash
python aep_schema_builder.py --create ../schemas/profile-schema.json
```

스키마만 생성 (데이터셋 제외):
```bash
python aep_schema_builder.py --create-all --no-datasets
```

### Step 6: 생성 확인

**스크립트로 확인:**
```bash
python aep_schema_builder.py --list
```

**AEP UI에서 확인:**
1. https://experience.adobe.com/ 접속
2. 왼쪽 메뉴 → Schemas 클릭
3. 다음 스키마 확인:
   - RTCDP Demo - Customer Profile
   - RTCDP Demo - Commerce Event
   - RTCDP Demo - Web Event
   - RTCDP Demo - Product Lookup

## 생성되는 리소스

### 1. Field Groups (4개)
- `RTCDP Demo - Customer Profile - Custom Fields`
- `RTCDP Demo - Commerce Event - Custom Fields`
- `RTCDP Demo - Web Event - Custom Fields`
- `RTCDP Demo - Product Lookup - Custom Fields`

### 2. Schemas (4개)

| Schema | Class | Profile 활성화 |
|--------|-------|---------------|
| RTCDP Demo - Customer Profile | XDM Individual Profile | ✓ |
| RTCDP Demo - Commerce Event | XDM Experience Event | ✓ |
| RTCDP Demo - Web Event | XDM Experience Event | ✓ |
| RTCDP Demo - Product Lookup | XDM Record | - |

### 3. Datasets (4개)
- `RTCDP Demo - Customer Profile Dataset`
- `RTCDP Demo - Commerce Event Dataset`
- `RTCDP Demo - Web Event Dataset`
- `RTCDP Demo - Product Lookup Dataset`

## 다음 단계

### 1. Identity Namespaces 생성 (AEP UI에서)

**경로:** Identities → Create identity namespace

생성할 네임스페이스:

| Display Name | Identity Symbol | Type |
|--------------|----------------|------|
| Customer ID | CustomerID | Cross-Device |
| Email | Email | Email |
| Phone | Phone | Phone |

**주의:** `ECID`는 AEP에 기본 제공되므로 생성 불필요

### 2. Primary Identity 설정 (AEP UI에서)

**경로:** Schemas → 스키마 선택 → Structure 탭

**Customer Profile Schema:**
1. `_rtcdpDemo` > `customerId` 필드 선택
2. Identity 체크박스 활성화
3. Identity namespace: `CustomerID` 선택
4. Primary identity 체크박스 활성화
5. Save

**Commerce Event Schema:**
- identityMap 사용 (별도 설정 불필요)

**Web Event Schema:**
- identityMap 사용 (별도 설정 불필요)

### 3. 데이터 수집 준비

**Batch Ingestion:**
```bash
# CSV 파일을 datasets에 매핑
# projects/rtcdp-demo/data/ 의 CSV 파일 사용
```

**Streaming Ingestion:**
```bash
# Web SDK 구현
# projects/rtcdp-demo/web-sdk/ 참조
```

## 문제 해결

### 인증 오류: "401 Unauthorized"

**원인:** Access Token 만료 (24시간 유효)

**해결:**
```bash
python auth_helper.py --generate-token
```

### 스키마가 이미 존재

**메시지:**
```
⚠ 스키마가 이미 존재합니다: https://ns.adobe.com/...
  생성을 건너뜁니다.
```

**해결:** 정상입니다. 중복 생성을 방지합니다.

기존 스키마를 삭제하고 재생성하려면:
1. AEP UI에서 스키마 수동 삭제
2. 스크립트 재실행

### Field Group 생성 실패

**원인:** Tenant 네임스페이스 충돌 또는 JSON 구조 오류

**해결:**
1. `.env`의 `TENANT_ID` 확인 (기본값: `_rtcdpDemo`)
2. 스키마 JSON 파일 검증
3. AEP UI에서 동일한 이름의 Field Group 확인

### Python 패키지 설치 오류

**패키지 설치 실패 시:**

```bash
# pip 업그레이드 후 재시도
pip install --upgrade pip
pip install -r requirements.txt
```

**macOS에서 설치 오류:**

```bash
# Xcode Command Line Tools 설치
xcode-select --install

# 재시도
pip3 install -r requirements.txt
```

## 추가 명령어

### 스키마 목록 조회
```bash
python aep_schema_builder.py --list
```

### Access Token 유효성 검증
```bash
python auth_helper.py --validate-token
```

### 도움말 보기
```bash
python aep_schema_builder.py --help
python auth_helper.py --help
```

## API Rate Limiting

Adobe Experience Platform API는 요청 횟수 제한이 있습니다:
- 스크립트는 자동으로 1초 간격으로 요청을 보냅니다
- 429 에러 발생 시 잠시 후 재시도하세요

## 보안 주의사항

1. **`.env` 파일을 Git에 커밋하지 마세요**
   - `.gitignore`에 이미 추가되어 있음
   - 민감한 인증 정보 포함

2. **Client Secret 보안 관리**
   - Git에 커밋 금지
   - 안전한 위치에 보관
   - 노출 시 즉시 Adobe Developer Console에서 재생성

3. **Access Token 노출 방지**
   - 로그나 에러 메시지 공유 시 토큰 삭제
   - 24시간 후 자동 만료

## 참고 자료

- [Adobe Experience Platform API 문서](https://www.adobe.io/apis/experienceplatform/home/api-reference.html)
- [Schema Registry API](https://www.adobe.io/apis/experienceplatform/home/api-reference.html#!acpdr/swagger-specs/schema-registry.yaml)
- [Adobe Developer Console](https://developer.adobe.com/console)
- [XDM Field Groups](https://experienceleague.adobe.com/docs/experience-platform/xdm/schema/composition.html)

## 지원

문제가 계속되면:
1. `README.md`의 문제 해결 섹션 확인
2. AEP UI에서 수동 스키마 생성 시도 (권한 확인)
3. Network 탭에서 API 응답 확인
