# Week 5-6: 세그멘테이션 및 오디언스

## 학습 목표
- Segmentation Service의 작동 원리 이해
- 다양한 세그먼트 유형 생성 및 평가
- 오디언스 활용 방법 학습

## 1. Segmentation Service

### 개념
고객 데이터를 기반으로 특정 조건을 만족하는 오디언스를 정의하고 자동으로 평가하는 서비스입니다.

### Segment Builder UI
시각적 세그먼트 빌더를 통해 코드 없이 세그먼트를 생성할 수 있습니다.

### 세그먼트 유형

#### Profile-Attribute 세그먼트
프로필의 속성 기반 세그먼트
- 예: "Premium 멤버십 고객"
- 예: "LA 거주 고객"

#### Event-Based 세그먼트
특정 이벤트 또는 행동 기반 세그먼트
- 예: "지난 30일 내 구매한 고객"
- 예: "웹사이트 이탈 고객"

#### Time-Based 세그먼트
시간 기반 조건이 포함된 세그먼트
- 예: "24시간 내 로그인하지 않은 고객"
- 예: "가입 후 7일 이내 첫 구매한 고객"

### 스트리밍 vs 배치 세그먼테이션

#### 스트리밍 세그먼테이션
- **장점**: 실시간 평가, 즉시 업데이트
- **용도**: 실시간 경고, 긴급 마케팅 캠페인
- **제한사항**: 복잡한 로직 제한, 높은 비용

#### 배치 세그먼테이션
- **장점**: 복잡한 로직 지원, 비용 효율적
- **용도**: 정기적인 캠페인, 복잡한 다중 단계 세그먼트
- **제한사항**: 주기적 업데이트 (일일/주간)

### PQL (Profile Query Language)
세그먼트를 정의하기 위한 전용 쿼리 언어입니다.

#### 기본 문법
```javascript
// 간단한 조건
SELECT user FROM profile WHERE user.loyaltyPoints > 1000

// 시간 기반 조건
SELECT user FROM profile WHERE user.lastPurchaseDate >= NOW() - INTERVAL 30 DAY

// 이벤트 기반
SELECT user FROM profile WHERE COUNT(user.events) > 5
```

### 실습 가이드
1. [행동 기반 세그먼트](./projects/week5-6/behavior-segment.md)
2. [인구통계 기반 세그먼트](./projects/week5-6/demographic-segment.md)
3. [다중 엔티티 세그먼트](./projects/week5-6/multi-entity-segment.md)

## 2. 오디언스 평가 방법

### Edge, Streaming, Batch 차이

#### Edge Segmentation
- 클라이언트 측에서 실시간 평가
- 최소 지연시간
- 개인화된 경험 제공에 적합

#### Streaming Segmentation
- 서버 측에서 실시간 평가
- 프로필 업데이트 시 즉시 재평가
- 실시간 알림, 마케팅에 적합

#### Batch Segmentation
- 주기적으로 대량 평가
- 복잡한 세그먼트에 적합
- 일일/주간 캠페인에 적합

### 세그먼트 작업 스케줄링
- **Daily**: 매일 새벽 평가
- **Weekly**: 매주 특정 요일 평가
- **On-demand**: 수동 실행

### 세그먼트 집계
- **전체 크기**: 세그먼트 조건을 만족하는 총 프로필 수
- **증분**: 마지막 평가 이후 새로 추가된 프로필 수
- **중복**: 여러 세그먼트 간 중복 프로필 수

### 실습 가이드
1. [스트리밍 세그먼트 성능 테스트](./projects/week5-6/streaming-performance.md)
2. [세그먼트 중복 분석](./projects/week5-6/segment-overlap.md)

## 3. Audience Composition (선택)

### 개념
여러 세그먼트를 조합하여 새로운 오디언스를 만드는 기능입니다.

### 사용 사례
- 세그먼트 교집합
- 세그먼트 합집합
- 특정 세그먼트 제외

## 학습 체크리스트

- [ ] Segment Builder UI로 세그먼트 생성 가능
- [ ] 행동 기반 세그먼트 생성 완료
- [ ] 인구통계 기반 세그먼트 생성 완료
- [ ] 다중 엔티티 세그먼트 생성 완료
- [ ] 스트리밍 vs 배치 차이 이해
- [ ] 세그먼트 중복 분석 완료
- [ ] 스트리밍 세그먼트 성능 테스트 완료

## 실습 프로젝트 요구사항

### 5가지 비즈니스 시나리오 세그먼트
1. **행동 기반**: 지난 7일 내 구매 전환한 고객
2. **행동 기반**: 장바구니를 버린 고객
3. **인구통계 기반**: Premium 멤버십 20대 여성 고객
4. **인구통계 기반**: 500포인트 이상 보유 고객
5. **다중 엔티티**: 특정 제품 카테고리 구매 + 특정 지역 거주 고객

## 참고 자료
- [Segmentation Service 개요](https://experienceleague.adobe.com/docs/experience-platform/segmentation/home.html)
- [Segment Builder 가이드](https://experienceleague.adobe.com/docs/experience-platform/segmentation/ui/overview.html)
- [PQL 참조](https://experienceleague.adobe.com/docs/experience-platform/segmentation/pql/overview.html)

