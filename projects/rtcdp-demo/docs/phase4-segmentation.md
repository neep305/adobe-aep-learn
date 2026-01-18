# Phase 4: 세그먼트 정의 (Segmentation)

## 개요

Real-Time Customer Data Platform의 핵심 기능인 오디언스 세그먼트를 생성합니다. 프로필 속성과 이벤트 데이터를 기반으로 비즈니스 시나리오에 맞는 5개의 세그먼트를 구축합니다.

---

## 세그먼트 평가 방식

| 평가 방식 | 특징 | 사용 사례 |
|----------|------|----------|
| **Edge** | 클라이언트 사이드 평가, 최저 지연시간 | 실시간 개인화 |
| **Streaming** | 서버 사이드 실시간 평가 | 실시간 마케팅 자동화 |
| **Batch** | 스케줄 기반 평가 (매일) | 복잡한 조건, 대량 처리 |

---

## 세그먼트 목록

### 1. VIP 고객 (VIP Customers)

**비즈니스 목적**: 최고 가치 고객 식별, VIP 전용 혜택 제공

**조건**:
- `membership_status = 'VIP'` **OR**
- `loyalty_points > 2000`

**평가 방식**: Batch

**PQL (Profile Query Language)**:
```
_rtcdpDemo.membershipStatus = "VIP" or _rtcdpDemo.loyaltyPoints > 2000
```

**예상 결과**: CUST003 (2100 points), CUST010 (VIP, 2200 points)

---

### 2. Premium 회원 (Premium Members)

**비즈니스 목적**: Premium 회원 대상 특별 프로모션

**조건**:
- `membership_status = 'Premium'`

**평가 방식**: Streaming

**PQL**:
```
_rtcdpDemo.membershipStatus = "Premium"
```

**예상 결과**: CUST001, CUST003, CUST005, CUST008

---

### 3. 최근 구매자 (Recent Purchasers)

**비즈니스 목적**: 30일 내 구매 고객 리텐션 마케팅

**조건**:
- 지난 30일 내 `commerce.purchases` 이벤트 존재

**평가 방식**: Streaming

**PQL**:
```
chain(xEvent, timestamp, [C0: WHAT(eventType = "commerce.purchases")])
  .filter(C0.timestamp occurs <= 30 days before now)
  .exists()
```

**Segment Builder UI 설정**:
1. Events 탭 선택
2. Commerce Purchases 이벤트 추가
3. Time frame: In last 30 days

---

### 4. 장바구니 이탈자 (Cart Abandoners)

**비즈니스 목적**: 장바구니에 상품 추가 후 구매하지 않은 고객 리타겟팅

**조건**:
- 지난 7일 내 `add_to_cart` 이벤트 존재 **AND**
- 해당 세션 이후 `purchase` 이벤트 없음

**평가 방식**: Streaming

**PQL**:
```
chain(xEvent, timestamp, [
  C0: WHAT(eventType = "commerce.productListAdds"),
  C1: WHAT(eventType = "commerce.purchases") WITHIN 24 hours AFTER C0
]).filter(C0.timestamp occurs <= 7 days before now).exists() = false
AND
chain(xEvent, timestamp, [
  C0: WHAT(eventType = "commerce.productListAdds")
]).filter(C0.timestamp occurs <= 7 days before now).exists()
```

**간소화된 조건** (Segment Builder UI):
1. Include: Add to cart event in last 7 days
2. Exclude: Purchase event after add to cart

---

### 5. 비활성 고객 (Inactive Customers)

**비즈니스 목적**: 90일 이상 활동 없는 고객 재활성화 캠페인

**조건**:
- 지난 90일 동안 어떤 이벤트도 없음
- Profile이 존재함 (과거 고객)

**평가 방식**: Batch

**PQL**:
```
not chain(xEvent, timestamp, [C0: WHAT(*)]).filter(C0.timestamp occurs <= 90 days before now).exists()
```

**Segment Builder UI 설정**:
1. All Events 선택
2. Time frame: NOT in last 90 days

---

## Segment Builder UI 상세 가이드

### 세그먼트 생성 단계

1. **Audiences > Create audience > Build rule**

2. **Canvas 구성**:
   - **Attributes**: 프로필 속성 조건
   - **Events**: 행동 이벤트 조건
   - **Audiences**: 기존 세그먼트 포함/제외

3. **조건 설정**:
   - Drag & Drop으로 필드 추가
   - 연산자 선택 (equals, contains, greater than 등)
   - AND/OR 논리 연산자 설정

4. **세그먼트 저장**:
   - Name 입력
   - Evaluation method 선택
   - Save

### 세그먼트 1: VIP 고객 UI 설정

```
┌─────────────────────────────────────────────────────────┐
│ Segment: VIP Customers                                  │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Container: Any                                       │ │
│ │                                                      │ │
│ │  ┌───────────────────────────────────────────────┐  │ │
│ │  │ _rtcdpDemo.membershipStatus equals "VIP"      │  │ │
│ │  └───────────────────────────────────────────────┘  │ │
│ │                       OR                             │ │
│ │  ┌───────────────────────────────────────────────┐  │ │
│ │  │ _rtcdpDemo.loyaltyPoints is greater than 2000 │  │ │
│ │  └───────────────────────────────────────────────┘  │ │
│ │                                                      │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ Evaluation: Batch                                       │
└─────────────────────────────────────────────────────────┘
```

### 세그먼트 4: 장바구니 이탈자 UI 설정

```
┌─────────────────────────────────────────────────────────┐
│ Segment: Cart Abandoners                                │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ INCLUDE                                              │ │
│ │  ┌───────────────────────────────────────────────┐  │ │
│ │  │ Event: productListAdds                        │  │ │
│ │  │ Time: In last 7 days                          │  │ │
│ │  └───────────────────────────────────────────────┘  │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ EXCLUDE                                              │ │
│ │  ┌───────────────────────────────────────────────┐  │ │
│ │  │ Event: purchases                              │  │ │
│ │  │ Time: After productListAdds                   │  │ │
│ │  └───────────────────────────────────────────────┘  │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ Evaluation: Streaming                                   │
└─────────────────────────────────────────────────────────┘
```

---

## API로 세그먼트 생성

### Segment Definition API

```bash
curl -X POST 'https://platform.adobe.io/data/core/ups/segment/definitions' \
  -H 'Authorization: Bearer {ACCESS_TOKEN}' \
  -H 'x-api-key: {API_KEY}' \
  -H 'x-gw-ims-org-id: {ORG_ID}' \
  -H 'x-sandbox-name: {SANDBOX_NAME}' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "VIP Customers",
    "description": "Customers with VIP status or loyalty points > 2000",
    "schema": {
      "name": "_xdm.context.profile"
    },
    "expression": {
      "type": "PQL",
      "format": "pql/text",
      "value": "_rtcdpDemo.membershipStatus = \"VIP\" or _rtcdpDemo.loyaltyPoints > 2000"
    },
    "evaluationInfo": {
      "batch": {
        "enabled": true
      }
    }
  }'
```

---

## 세그먼트 모니터링

### Population 확인

1. **Audiences > 해당 세그먼트 선택**
2. **Overview** 탭에서 확인:
   - Total profiles (전체 프로필 수)
   - Qualified profiles (조건 충족)
   - Existing profiles (기존 멤버)
   - New profiles (신규 진입)
   - Exited profiles (이탈)

### 세그먼트별 예상 Population

| 세그먼트 | 예상 프로필 수 | 고객 ID |
|----------|---------------|---------|
| VIP Customers | 2 | CUST003, CUST010 |
| Premium Members | 4 | CUST001, CUST003, CUST005, CUST008 |
| Recent Purchasers | 10 | 모든 고객 (샘플 데이터 기준) |
| Cart Abandoners | 1 | 12345 (웹 이벤트 기준) |
| Inactive Customers | 0 | 없음 (최근 데이터만 존재) |

---

## 세그먼트 조합 전략

### 중첩 세그먼트 활용

```
┌─────────────────────────────────────────────────────┐
│                    모든 고객                         │
│                                                     │
│   ┌───────────────────┐   ┌───────────────────┐    │
│   │  VIP Customers    │   │ Premium Members   │    │
│   │    (2명)          │   │    (4명)          │    │
│   │  ┌─────────────┐  │   │                   │    │
│   │  │ 고가치 VIP  │  │   │                   │    │
│   │  │ (CUST003)   │  │   │                   │    │
│   │  └─────────────┘  │   │                   │    │
│   └───────────────────┘   └───────────────────┘    │
│                                                     │
│   ┌─────────────────────────────────────────────┐  │
│   │           Cart Abandoners                    │  │
│   │              (1명)                           │  │
│   └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 마케팅 시나리오별 세그먼트

| 시나리오 | 사용 세그먼트 | 조합 |
|----------|--------------|------|
| VIP 전용 혜택 | VIP Customers | 단일 |
| 업셀링 캠페인 | Premium Members + Recent Purchasers | AND |
| 재구매 유도 | Cart Abandoners - Recent Purchasers | EXCLUDE |
| 재활성화 | Inactive Customers | 단일 |

---

## 세그먼트 테스트

### Profile Preview

1. 세그먼트 편집 화면에서 **Estimate** 클릭
2. 예상 프로필 수 확인
3. **View profiles** 클릭
4. 샘플 프로필 상세 확인

### Profile Lookup으로 검증

1. **Profiles > Browse**
2. Identity 값 입력 (예: john.doe@example.com)
3. **Segment membership** 탭 확인
4. 해당 프로필이 속한 세그먼트 목록 확인

---

## 완료 체크리스트

- [ ] VIP Customers 세그먼트 생성 완료
- [ ] Premium Members 세그먼트 생성 완료
- [ ] Recent Purchasers 세그먼트 생성 완료
- [ ] Cart Abandoners 세그먼트 생성 완료
- [ ] Inactive Customers 세그먼트 생성 완료
- [ ] 각 세그먼트 Population 확인
- [ ] Profile에서 Segment membership 확인

---

## 다음 단계

세그먼트 정의가 완료되면 [Phase 5: 데모 웹사이트](phase5-web-demo.md)로 진행합니다.
