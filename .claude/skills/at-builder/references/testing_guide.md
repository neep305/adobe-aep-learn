# A/B 테스트 및 MVT 설계 가이드

## 목차

1. [A/B 테스트 설계](#ab-테스트-설계)
2. [다변량 테스트 (MVT)](#다변량-테스트-mvt)
3. [Auto-Allocate 및 Auto-Target](#auto-allocate-및-auto-target)
4. [Experience Targeting (XT)](#experience-targeting-xt)
5. [Recommendations](#recommendations)
6. [테스트 결과 분석](#테스트-결과-분석)

---

## A/B 테스트 설계

### 가설 프레임워크

```
"만약 [변경 사항]을 적용하면,
 [측정 지표]가 [방향]할 것이다.
 왜냐하면 [이유/근거]이기 때문이다."

예시:
"만약 CTA 버튼 색상을 파란색에서 주황색으로 변경하면,
 클릭률이 증가할 것이다.
 왜냐하면 주황색이 현재 페이지 색상 구성에서 더 눈에 띄기 때문이다."
```

### VEC (Visual Experience Composer) 활용

1. **요소 수정**
   - 텍스트 변경: 클릭 → Edit Text
   - 이미지 변경: 클릭 → Replace Image → URL 입력
   - 스타일 변경: 클릭 → Edit HTML → CSS 수정

2. **레이아웃 변경**
   - 요소 이동: Drag & Drop
   - 요소 순서 변경: Move Element
   - 요소 숨기기: Hide

3. **코드 기반 변경**
   ```javascript
   // Custom Code 삽입 예시
   document.querySelector('.hero-title').textContent = '새로운 제목';
   document.querySelector('.cta-btn').style.backgroundColor = '#FF6600';
   ```

### 경험(Experience) 설정

```yaml
Experience A (Control - 대조군):
  - 현재 페이지 그대로
  - 트래픽 비율: 50%

Experience B (Treatment - 변형):
  - 변경 사항 적용
  - 트래픽 비율: 50%
```

### 목표(Goal) 설정 유형

| 목표 유형 | 용도 | 예시 |
|----------|------|------|
| Conversion | 특정 페이지 도달 | 결제 완료 페이지 방문 |
| Clicked an Element | 특정 요소 클릭 | CTA 버튼 클릭 |
| Viewed an mbox | mbox 노출 | 폼 제출 완료 mbox |
| Revenue | 구매 금액 | 주문 총액 |
| Engagement | 체류 시간/페이지뷰 | 사이트 참여도 |

### 보조 목표 설정

```yaml
Primary Goal:
  - 전환율 (구매 완료)

Secondary Goals:
  - 클릭률 (CTA 클릭)
  - 장바구니 추가율
  - 평균 주문 금액
```

---

## 다변량 테스트 (MVT)

### MVT vs A/B 테스트

| 항목 | A/B 테스트 | MVT |
|------|-----------|-----|
| 테스트 범위 | 하나의 변경 | 여러 요소 조합 |
| 트래픽 요구량 | 낮음 | 높음 |
| 인사이트 | 단순 비교 | 상호작용 효과 |
| 복잡도 | 낮음 | 높음 |

### MVT 설계 예시

```yaml
테스트 요소:
  헤드라인:
    - A: "무료 배송"
    - B: "오늘만 할인"
    - C: "신규 회원 혜택"

  이미지:
    - X: 제품 이미지
    - Y: 라이프스타일 이미지

  버튼 색상:
    - 1: 파란색
    - 2: 주황색

조합 수: 3 × 2 × 2 = 12개 경험
필요 트래픽: 약 12 × 3,000 = 36,000 방문자
```

### MVT 분석 결과 해석

```
요소별 기여도 (Element Contribution):
┌─────────────┬──────────────┬─────────────┐
│ 요소        │ 기여도       │ 신뢰도      │
├─────────────┼──────────────┼─────────────┤
│ 헤드라인    │ 45%          │ 95%         │
│ 이미지      │ 35%          │ 92%         │
│ 버튼 색상   │ 20%          │ 88%         │
└─────────────┴──────────────┴─────────────┘

최적 조합: 헤드라인 B + 이미지 Y + 버튼 2
예상 전환율 향상: +23%
```

---

## Auto-Allocate 및 Auto-Target

### Auto-Allocate

자동으로 더 성과 좋은 경험에 트래픽 재배분.

```yaml
설정:
  - 최소 탐색 트래픽: 10% (각 경험에 할당)
  - 나머지 트래픽: 성과 기반 동적 배분

장점:
  - 기회 비용 감소
  - 빠른 승자 결정
  - 통계적 유의성 자동 판단

주의사항:
  - 최소 50 전환/경험 필요
  - 시작 후 경험 변경 불가
```

### Auto-Target (ML 기반 개인화)

방문자 프로필 기반으로 최적 경험 자동 선택.

```yaml
활용 데이터:
  - 방문자 속성 (브라우저, 디바이스, 지역)
  - 방문 이력 (이전 페이지뷰, 구매 기록)
  - 세션 정보 (유입 채널, 검색어)

모델 학습:
  - 최소 1,000 방문자/경험 후 시작
  - 지속적 모델 업데이트
  - 랜덤 포레스트 기반 예측
```

### 알고리즘 선택 가이드

```
시작
  │
  ├─ 트래픽이 충분한가? (>50K/월)
  │     │
  │     ├─ Yes: 개인화가 필요한가?
  │     │         │
  │     │         ├─ Yes → Auto-Target
  │     │         └─ No → Auto-Allocate
  │     │
  │     └─ No: A/B Test (수동)
  │
  └─ 세그먼트별 경험이 명확한가?
        │
        ├─ Yes → Experience Targeting (XT)
        └─ No → A/B Test
```

---

## Experience Targeting (XT)

### 대상자 기반 경험 매핑

```yaml
대상자 정의:
  - VIP 고객:
      조건: profile.memberTier == "VIP"
      경험: VIP 전용 혜택 배너

  - 신규 방문자:
      조건: profile.visitCount == 1
      경험: 신규 회원 가입 프로모션

  - 재방문 고객:
      조건: profile.visitCount > 5
      경험: 재구매 할인 쿠폰

  - 기본값:
      조건: All Other Visitors
      경험: 일반 프로모션
```

### 우선순위 설정

```
1순위: VIP 고객 (가장 높은 우선순위)
   ↓
2순위: 신규 방문자
   ↓
3순위: 재방문 고객
   ↓
4순위: 기본값 (fallback)
```

### XT vs A/B 테스트

| 상황 | 권장 활동 |
|------|----------|
| 가설 검증이 필요함 | A/B 테스트 |
| 최적 경험을 모름 | A/B 테스트 |
| 세그먼트별 경험이 명확함 | XT |
| 빠른 개인화 적용 | XT |

---

## Recommendations

### 알고리즘 유형

| 알고리즘 | 용도 | 특징 |
|----------|------|------|
| Recently Viewed | 최근 본 상품 | 개인화, 리타겟팅 |
| Most Viewed | 인기 상품 | 콜드 스타트 해결 |
| Bought This, Bought That | 교차 판매 | 구매 패턴 기반 |
| Viewed This, Viewed That | 연관 상품 | 브라우징 패턴 |
| Custom Algorithm | 커스텀 로직 | 비즈니스 규칙 적용 |

### 엔티티(Entity) 속성 설정

```javascript
// 상품 상세 페이지에서 엔티티 정보 전달
adobe.target.trackEvent({
  mbox: "productPage",
  params: {
    "entity.id": "SKU123",
    "entity.name": "프리미엄 헤드폰",
    "entity.categoryId": "electronics,audio,headphones",
    "entity.brand": "SoundMax",
    "entity.value": 299000,
    "entity.inventory": 50,
    "entity.thumbnailUrl": "https://example.com/img/sku123.jpg",
    "entity.pageUrl": window.location.href
  }
});
```

### 디자인 템플릿

```html
<!-- Velocity 템플릿 예시 -->
<div class="recs-container">
  #foreach($product in $recommendations)
    <div class="rec-item" data-entity-id="$product.id">
      <img src="$product.thumbnailUrl" alt="$product.name">
      <h4>$product.name</h4>
      <p class="price">₩$product.value</p>
      <a href="$product.pageUrl">자세히 보기</a>
    </div>
  #end
</div>
```

---

## 테스트 결과 분석

### 통계적 유의성 이해

```
신뢰 수준 (Confidence Level):
  - 95%: 표준 (5% 오류 확률)
  - 99%: 엄격 (1% 오류 확률)

상승률 (Lift):
  상승률 = (변형 전환율 - 대조군 전환율) / 대조군 전환율 × 100%

예시:
  대조군: 5.0% 전환율
  변형: 6.0% 전환율
  상승률: (6.0 - 5.0) / 5.0 × 100 = +20%
```

### 신뢰 구간 해석

```
변형 B 결과:
  전환율: 6.0%
  신뢰 구간 (95%): [5.2%, 6.8%]
  대조군 대비 상승률: +20%

해석:
  - 6.8% > 5.0% (대조군): 통계적으로 유의미
  - 하한이 대조군보다 높으면 → 승자로 선언 가능
```

### 결과 보고서 템플릿

```markdown
## A/B 테스트 결과 보고서

### 테스트 개요
- 테스트명: 홈페이지 히어로 배너 A/B 테스트
- 기간: 2025-01-01 ~ 2025-01-14
- 총 방문자: 45,000
- 목표: CTA 클릭률 향상

### 결과 요약
| 경험 | 방문자 | 전환 | 전환율 | 신뢰도 |
|------|--------|------|--------|--------|
| 대조군 | 22,500 | 900 | 4.0% | - |
| 변형 B | 22,500 | 1,125 | 5.0% | 98% |

### 인사이트
- 변형 B가 대조군 대비 +25% 상승률 달성
- 98% 신뢰도로 통계적으로 유의미
- 모바일에서 특히 높은 성과 (+35%)

### 권장 사항
- 변형 B를 전체 트래픽에 적용
- 모바일 경험 추가 최적화 테스트 고려
```

### 세그먼트별 분석

```yaml
전체:
  대조군: 4.0%
  변형: 5.0%
  상승률: +25%

디바이스별:
  데스크톱:
    대조군: 4.5%
    변형: 5.2%
    상승률: +15%

  모바일:
    대조군: 3.5%
    변형: 4.7%
    상승률: +35%

트래픽 소스별:
  유기적 검색:
    대조군: 5.0%
    변형: 6.5%
    상승률: +30%

  직접 방문:
    대조군: 3.0%
    변형: 3.5%
    상승률: +17%
```

### 테스트 실패 시 체크리스트

```
□ 충분한 샘플 크기 확보했는가?
□ 테스트 기간이 1-2주 이상이었는가?
□ 시즌/이벤트 영향을 고려했는가?
□ 세그먼트별로 다른 결과가 있는가?
□ 구현이 올바르게 되었는가 (QA 검증)?
□ 전환 추적이 정확한가?
□ 가설이 명확했는가?
```
