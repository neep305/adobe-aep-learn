# Phase 6: Activation (활성화)

## 개요

세그먼트를 외부 마케팅 채널로 활성화(Activation)합니다. 이 과정을 통해 AEP에서 정의한 오디언스를 광고 플랫폼, 이메일 마케팅, CRM 등에서 활용할 수 있습니다.

---

## Destination 유형

| 유형 | 특징 | 예시 |
|------|------|------|
| **Streaming** | 실시간 프로필/세그먼트 전송 | Google Ads, Facebook, HTTP API |
| **Batch** | 스케줄 기반 파일 내보내기 | Cloud Storage, Email Platform |
| **Edge** | 초저지연 개인화 | Personalization engines |

---

## 테스트용 HTTP API Destination

프로덕션 연동 전 테스트를 위한 HTTP API Destination을 설정합니다.

### Webhook 테스트 서비스 사용

무료 webhook 테스트 서비스 활용:
- webhook.site
- requestbin.com
- beeceptor.com

### HTTP API Destination 설정

1. **Destinations > Catalog > HTTP API**
2. **Configure** 클릭
3. 설정 입력:

```
Name: RTCDP Demo - HTTP Endpoint
Description: Test destination for RTCDP demo
Endpoint URL: https://webhook.site/your-unique-id
Authentication: None (테스트용)
```

4. **Mapping 설정**:

| Source Field | Target Field |
|-------------|-------------|
| `segmentMembership` | `segments` |
| `identityMap.Email` | `email` |
| `identityMap.CustomerID` | `customer_id` |
| `person.name.firstName` | `first_name` |
| `person.name.lastName` | `last_name` |

5. **Schedule**:
- Frequency: Hourly (테스트용)
- Export full files: Yes

---

## Streaming Destination: Google Ads

### 사전 요구사항
- Google Ads 계정
- Customer Match 사용 권한
- Google Ads Customer ID

### 연결 설정

1. **Destinations > Catalog > Google Ads**
2. **Connect destination**
3. Google 계정 인증
4. 설정:

```
Account Type: Invite users to an existing Customer list
Customer Account ID: 123-456-7890
Audience Name Prefix: RTCDP_Demo_
```

### 세그먼트 활성화

1. **Audiences > 세그먼트 선택**
2. **Activate** 클릭
3. Destination 선택: Google Ads
4. Identity 매핑:
   - Email → Google Email
   - Phone → Google Phone Number
5. 스케줄 설정

### Google Ads에서 확인
- Audience Manager에서 Customer Match 리스트 확인
- 예상 도달 범위 확인

---

## Batch Destination: Cloud Storage

### Amazon S3 설정

1. **Destinations > Catalog > Amazon S3**
2. **Connect destination**
3. 인증 정보:

```
Bucket name: rtcdp-demo-exports
Folder path: /audiences
Access Key: YOUR_ACCESS_KEY
Secret Key: YOUR_SECRET_KEY
```

4. 파일 형식:
   - Format: JSON 또는 CSV
   - Compression: GZIP

### 내보내기 스케줄

```
Export frequency: Daily
Export time: 00:00 UTC
Include incremental: Yes
Include headers: Yes
```

### 내보내기 파일 구조

```json
{
  "profiles": [
    {
      "identities": {
        "Email": "john.doe@example.com",
        "CustomerID": "CUST001"
      },
      "attributes": {
        "firstName": "John",
        "lastName": "Doe",
        "loyaltyPoints": 1250,
        "membershipStatus": "Premium"
      },
      "segments": [
        {
          "id": "segment-123",
          "name": "Premium Members",
          "status": "realized"
        }
      ]
    }
  ]
}
```

---

## 세그먼트별 활성화 전략

### 1. VIP Customers → Google Ads
**목적**: VIP 대상 특별 프로모션 광고

```
Destination: Google Ads
Identity: Email
Frequency: Every 3 hours
Use Case: Similar Audience 생성, 리타겟팅
```

### 2. Premium Members → Email Platform
**목적**: 멤버십 뉴스레터, 프로모션 이메일

```
Destination: Email Platform (Mailchimp, Salesforce MC)
Identity: Email
Frequency: Daily
Use Case: 이메일 마케팅 캠페인
```

### 3. Cart Abandoners → HTTP API
**목적**: 실시간 장바구니 이탈 알림

```
Destination: HTTP API (마케팅 자동화 시스템)
Identity: Email, CustomerID
Frequency: Real-time (Streaming)
Use Case: 자동 리마인더 이메일, 푸시 알림
```

### 4. Inactive Customers → CRM
**목적**: 재활성화 캠페인 리스트

```
Destination: Salesforce CRM
Identity: CustomerID
Frequency: Weekly
Use Case: 세일즈 팀 아웃리치
```

---

## Activation Flow 모니터링

### Dataflow 확인

1. **Monitoring > Dataflows**
2. Destination 선택
3. 확인 항목:
   - Records received (수신된 레코드)
   - Records activated (활성화된 레코드)
   - Records failed (실패한 레코드)
   - Last run time

### 성공 지표

| 지표 | 정상 범위 | 확인 방법 |
|------|----------|----------|
| Success rate | > 95% | Monitoring 대시보드 |
| Latency | < 5분 (Streaming) | Dataflow 상세 |
| Records matched | > 80% | Destination 보고서 |

### 에러 처리

**일반적인 에러**:

| 에러 | 원인 | 해결 방법 |
|------|------|----------|
| Identity not found | 필수 Identity 없음 | Identity 매핑 확인 |
| Rate limit exceeded | API 호출 제한 초과 | 빈도 조정 |
| Authentication failed | 인증 만료 | Destination 재인증 |
| Invalid format | 필드 형식 불일치 | 매핑 검토 |

---

## API로 Activation 관리

### Dataflow 조회

```bash
curl -X GET 'https://platform.adobe.io/data/foundation/flowservice/flows' \
  -H 'Authorization: Bearer {ACCESS_TOKEN}' \
  -H 'x-api-key: {API_KEY}' \
  -H 'x-gw-ims-org-id: {ORG_ID}' \
  -H 'x-sandbox-name: {SANDBOX_NAME}'
```

### 세그먼트 Activation 상태 조회

```bash
curl -X GET 'https://platform.adobe.io/data/core/ups/segment/jobs' \
  -H 'Authorization: Bearer {ACCESS_TOKEN}' \
  -H 'x-api-key: {API_KEY}' \
  -H 'x-gw-ims-org-id: {ORG_ID}' \
  -H 'x-sandbox-name: {SANDBOX_NAME}'
```

---

## 활성화 워크플로우

### 전체 프로세스

```
┌─────────────────────────────────────────────────────────────────┐
│                        AEP Platform                              │
│                                                                  │
│  ┌──────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐ │
│  │ Profile  │───►│ Segment   │───►│ Activation│───►│ Export   │ │
│  │ Updates  │    │ Evaluation│    │ Service   │    │ Queue    │ │
│  └──────────┘    └───────────┘    └───────────┘    └────┬─────┘ │
│                                                          │       │
└──────────────────────────────────────────────────────────┼───────┘
                                                           │
         ┌─────────────────────────────────────────────────┼───────┐
         │                                                 ▼       │
         │  ┌───────────┐  ┌───────────┐  ┌───────────┐           │
         │  │ Google    │  │ Email     │  │ HTTP      │           │
         │  │ Ads       │  │ Platform  │  │ API       │           │
         │  └───────────┘  └───────────┘  └───────────┘           │
         │                  Destinations                           │
         └─────────────────────────────────────────────────────────┘
```

### 타임라인

| 단계 | Streaming | Batch |
|------|-----------|-------|
| 프로필 업데이트 | 즉시 | 축적 |
| 세그먼트 평가 | 실시간 | 스케줄 |
| Destination 전송 | 분 단위 | 시간 단위 |
| Destination 수신 | 즉시 | 파일 처리 |

---

## 데모 시나리오 검증

### 시나리오 1: 실시간 세그먼트 활성화

1. 웹사이트에서 로그인 (jane.smith@example.com)
2. 상품 조회 및 장바구니 추가
3. 구매하지 않고 이탈
4. Cart Abandoners 세그먼트 진입 확인
5. HTTP API Destination에서 데이터 수신 확인

**예상 Webhook 수신 데이터**:
```json
{
  "email": "jane.smith@example.com",
  "customer_id": "CUST002",
  "first_name": "Jane",
  "last_name": "Smith",
  "segments": [
    {
      "id": "cart-abandoners-segment-id",
      "name": "Cart Abandoners",
      "status": "realized",
      "timestamp": "2023-10-15T10:30:00Z"
    }
  ]
}
```

### 시나리오 2: Batch Export 검증

1. VIP Customers 세그먼트 확인 (2명)
2. Cloud Storage Destination으로 내보내기 실행
3. S3 버킷에서 파일 확인
4. 파일 내용 검증

---

## 완료 체크리스트

- [ ] HTTP API Destination 설정 완료
- [ ] 테스트 세그먼트 활성화 완료
- [ ] Webhook에서 데이터 수신 확인
- [ ] (선택) Google Ads Destination 연결
- [ ] (선택) Cloud Storage Destination 연결
- [ ] Monitoring에서 Dataflow 상태 확인
- [ ] 에러 발생 시 해결 완료

---

## 프로젝트 완료!

모든 Phase를 완료했습니다.

### 구축된 RTCDP 데모 환경

| 구성 요소 | 수량 | 상태 |
|----------|------|------|
| XDM Schemas | 4개 | ✅ |
| Identity Namespaces | 3개 | ✅ |
| Datasets | 4개 | ✅ |
| Segments | 5개 | ✅ |
| Web Demo Pages | 4개 | ✅ |
| Destinations | 1-3개 | ✅ |

### 다음 학습 주제

- [ ] Edge Segmentation 심화
- [ ] Offer Decisioning 연동
- [ ] Adobe Journey Optimizer 통합
- [ ] Query Service 고급 분석
- [ ] Data Governance 정책 적용

---

## 참고 자료

- [Destinations 문서](https://experienceleague.adobe.com/docs/experience-platform/destinations/home.html)
- [Destination Catalog](https://experienceleague.adobe.com/docs/experience-platform/destinations/catalog/overview.html)
- [Activation API](https://developer.adobe.com/experience-platform-apis/references/destinations/)
- [Monitoring 가이드](https://experienceleague.adobe.com/docs/experience-platform/dataflows/ui/monitor-destinations.html)
