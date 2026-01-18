# Phase 2: Identity 설정

## 개요

Identity Service는 고객의 다양한 식별자(이메일, 전화번호, 쿠키 ID 등)를 연결하여 통합된 고객 프로필을 생성합니다. 이 가이드에서는 RTCDP 데모에 필요한 Identity Namespace를 설정합니다.

---

## Identity 개념

### Identity Namespace
식별자의 유형을 정의합니다. 예: Email, Phone, CRM ID 등

### Identity Graph
동일 고객의 여러 식별자를 연결하는 그래프 구조입니다.

```
                    ┌─────────────────┐
                    │   고객 A        │
                    │   Profile       │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌─────▼─────┐        ┌─────▼─────┐
   │ ECID    │         │ Email     │        │ CustomerID│
   │ abc123  │◄───────►│ john@...  │◄──────►│ CUST001   │
   └─────────┘         └───────────┘        └───────────┘
   (웹 브라우저)         (로그인 시)          (CRM 시스템)
```

---

## 필요한 Identity Namespace

### 1. Standard Namespaces (기본 제공)

| Namespace | Code | Type | 설명 |
|-----------|------|------|------|
| Email | Email | Email | 이메일 주소 |
| Phone | Phone | Phone | 전화번호 |
| ECID | ECID | Cookie | Experience Cloud ID (웹 쿠키) |

### 2. Custom Namespace (생성 필요)

| Namespace | Code | Type | 설명 |
|-----------|------|------|------|
| CustomerID | customerid | Non-people identifier | CRM 고객 ID |

---

## Custom Identity Namespace 생성

### AEP UI에서 생성

1. **Identities** 메뉴로 이동
2. **Create identity namespace** 클릭
3. 다음 정보 입력:

**CustomerID Namespace**
```
Display name: CustomerID
Identity symbol: customerid
Type: Non-people identifier
Description: CRM Customer ID for RTCDP Demo
```

### API로 생성

```bash
curl -X POST 'https://platform.adobe.io/data/core/idnamespace/identities' \
  -H 'Authorization: Bearer {ACCESS_TOKEN}' \
  -H 'x-api-key: {API_KEY}' \
  -H 'x-gw-ims-org-id: {ORG_ID}' \
  -H 'x-sandbox-name: {SANDBOX_NAME}' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "CustomerID",
    "code": "customerid",
    "idType": "NON_PEOPLE_IDENTIFIER",
    "description": "CRM Customer ID for RTCDP Demo"
  }'
```

---

## Identity 매핑 전략

### 샘플 데이터의 Identity 필드

| 데이터 소스 | 필드 | Identity Namespace |
|-------------|------|-------------------|
| customer.csv | customer_id | CustomerID |
| customer.csv | email | Email |
| customer.csv | phone | Phone |
| order.csv | customer_id | CustomerID |
| sample-web-events.csv | personId | ECID |

### Identity Graph 시나리오

**시나리오 1: 신규 웹 방문자**
```
1. 사용자가 웹사이트 최초 방문
2. ECID 자동 생성 (예: 12345)
3. Profile 생성: ECID만 존재
```

**시나리오 2: 로그인 사용자**
```
1. 사용자가 로그인 (email: john@example.com)
2. ECID와 Email 연결
3. Identity Graph: ECID ↔ Email
```

**시나리오 3: 구매 완료**
```
1. 고객이 구매 (CustomerID: CUST001)
2. CustomerID가 Identity Graph에 추가
3. Identity Graph: ECID ↔ Email ↔ CustomerID
```

---

## 스키마별 Identity 설정

### Customer Profile Schema
```json
{
  "identities": [
    {
      "field": "_rtcdpDemo.customerId",
      "namespace": "customerid",
      "primary": true
    },
    {
      "field": "personalEmail.address",
      "namespace": "Email",
      "primary": false
    },
    {
      "field": "mobilePhone.number",
      "namespace": "Phone",
      "primary": false
    }
  ]
}
```

### Commerce Event Schema
```json
{
  "identityMap": {
    "CustomerID": [
      {
        "id": "CUST001",
        "primary": true
      }
    ]
  }
}
```

### Web Event Schema
```json
{
  "identityMap": {
    "ECID": [
      {
        "id": "12345",
        "primary": true
      }
    ],
    "Email": [
      {
        "id": "john@example.com",
        "primary": false
      }
    ]
  }
}
```

---

## Identity Graph 예시

샘플 데이터 기준 예상 Identity Graph:

### 고객 1 (John Doe)
```
┌─────────────────────────────────────────────────┐
│                 Identity Graph                   │
│                                                  │
│   CustomerID: CUST001                           │
│        │                                         │
│        ├──── Email: john.doe@example.com        │
│        │                                         │
│        └──── Phone: +1234567890                 │
│                                                  │
│   (웹 방문 시 ECID도 연결됨)                     │
└─────────────────────────────────────────────────┘
```

### 통합 프로필 결과
```json
{
  "identityGraph": {
    "nodes": [
      { "namespace": "CustomerID", "id": "CUST001" },
      { "namespace": "Email", "id": "john.doe@example.com" },
      { "namespace": "Phone", "id": "+1234567890" }
    ],
    "edges": [
      { "source": "CustomerID", "target": "Email" },
      { "source": "CustomerID", "target": "Phone" }
    ]
  },
  "profile": {
    "person": {
      "name": {
        "firstName": "John",
        "lastName": "Doe"
      }
    },
    "_rtcdpDemo": {
      "customerId": "CUST001",
      "membershipStatus": "Premium",
      "loyaltyPoints": 1250
    }
  }
}
```

---

## Identity 설정 우선순위

### Primary Identity 선택 기준

1. **가장 안정적인 식별자** 선택
   - CRM ID > Email > Phone > ECID

2. **Cross-device 추적이 필요한 경우**
   - 로그인 기반 ID (Email, CustomerID) 우선

3. **익명 사용자 추적이 중요한 경우**
   - ECID를 Primary로 설정

### RTCDP 데모 권장 설정

| 스키마 | Primary Identity | 이유 |
|--------|-----------------|------|
| Customer Profile | CustomerID | CRM 마스터 데이터 기준 |
| Commerce Event | CustomerID | 주문은 인증된 고객만 |
| Web Event | ECID | 익명 방문자 포함 |

---

## Merge Policy 설정

### Merge Policy 생성

1. **Profiles > Merge policies > Create merge policy**
2. 설정:
   - Name: `RTCDP Demo Merge Policy`
   - ID stitching: Private Graph
   - Attribute merge: Timestamp ordered (최신 데이터 우선)

### Merge Policy 옵션

| 옵션 | 설명 | 권장 상황 |
|------|------|----------|
| Timestamp ordered | 최신 타임스탬프 데이터 우선 | 실시간 업데이트 중요 |
| Dataset precedence | 지정 데이터셋 우선 | 마스터 데이터 소스 지정 |
| Private Graph | 조직 전용 Identity Graph | 기본 권장 |
| Shared Graph | Adobe 공유 그래프 | 외부 데이터 통합 |

---

## 완료 체크리스트

- [ ] CustomerID Namespace 생성 완료
- [ ] 기존 Standard Namespace 확인 (Email, Phone, ECID)
- [ ] 각 스키마에 Identity 설정 완료
- [ ] Merge Policy 생성 완료
- [ ] Identity Graph 테스트 (샘플 데이터 수집 후)

---

## 다음 단계

Identity 설정이 완료되면 [Phase 3: 데이터 수집](phase3-data-ingestion.md)으로 진행합니다.
