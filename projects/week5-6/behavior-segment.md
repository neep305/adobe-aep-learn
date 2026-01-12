# 실습: 행동 기반 세그먼트 생성

## 목표
고객의 웹 행동을 기반으로 세그먼트를 생성합니다.

## 시나리오
"지난 7일 내에 웹사이트를 방문했지만 구매하지 않은 고객" 세그먼트 생성

## 1. UI에서 세그먼트 생성

### 세그먼트 이름
"Recent Visitors No Purchase"

### 조건 설정

#### 1단계: 최근 방문자 필터
1. Segment Builder에서 **Add Container** 클릭
2. **Event** 선택
3. Event 조건:
   - Schema: Web Page View Event
   - Event Type: `web.webpagedetails.pageViews`
   - Time Range: **Last 7 days**

#### 2단계: 구매하지 않은 고객 필터
1. **Add Container** 클릭
2. **Profile** 선택
3. 조건 추가:
   - Exclude Container
   - Event
   - Event Type: `commerce.purchases`
   - Time Range: **Last 7 days**

### 논리 구조
```
(Last 7 days page view) AND NOT (Last 7 days purchase)
```

## 2. API를 통한 세그먼트 생성 (선택)

```json
POST https://platform.adobe.io/data/core/ups/segment/definitions
Headers:
  Authorization: Bearer {accessToken}
  Content-Type: application/json

Body:
{
  "name": "Recent Visitors No Purchase",
  "description": "Visitors in last 7 days who didn't purchase",
  "expression": {
    "type": "PQL",
    "format": "pql/text",
    "value": "not(exists(XDM_SEGMENT_TIMEOUT, true)) AND exists(YOUR_SCHEMA.eventType, x -> x = 'web.webpagedetails.pageViews' AND timestamp >= NOW() - INTERVAL 7 DAY) AND not(exists(YOUR_SCHEMA.eventType, x -> x = 'commerce.purchases' AND timestamp >= NOW() - INTERVAL 7 DAY))"
  },
  "schema": {
    "name": "_xdm.context.profile"
  },
  "ttlInDays": 60
}
```

## 3. 세그먼트 평가

### 수동 평가
1. 세그먼트 상세 페이지에서 **Evaluate** 클릭
2. 평가 방법 선택:
   - **Full**: 전체 데이터셋 재평가
   - **Incremental**: 마지막 평가 이후 변경사항만 평가

### 스케줄 설정
1. **Schedule** 메뉴 선택
2. 평가 주기 설정:
   - **Daily**: 매일 새벽
   - **Weekly**: 매주 특정 요일
3. Save

## 4. 결과 확인

### 세그먼트 집계
1. 세그먼트 상세 페이지에서 집계 확인
2. 다음 정보 확인:
   - 총 프로필 수
   - 증분 프로필 수
   - 마지막 평가 시간

### 샘플 프로필 확인
1. **View Sample Profiles** 클릭
2. 세그먼트에 포함된 프로필 샘플 확인
3. 프로필 상세 정보 확인

## 검증

생성된 세그먼트가 다음 조건을 만족하는지 확인:
- [ ] 지난 7일 내 페이지뷰 이벤트가 있는 고객 포함
- [ ] 지난 7일 내 구매 이벤트가 있는 고객 제외
- [ ] 세그먼트 집계에 프로필이 포함됨
- [ ] 샘플 프로필에서 조건이 만족됨

## 추가 실습

### 시나리오 2: 장바구니를 버린 고객
조건:
- 장바구니에 상품 추가 이벤트 발생
- 구매 이벤트 미발생
- 시간 범위: 지난 30일

### 시나리오 3: VIP 고객
조건:
- 총 구매 금액 $1000 이상
- 또는 loyaltyPoints 5000 이상

## 다음 단계
- [인구통계 기반 세그먼트](./demographic-segment.md)

