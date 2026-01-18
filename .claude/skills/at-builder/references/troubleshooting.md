# Adobe Target 문제 해결 가이드

## 목차

1. [구현 문제](#구현-문제)
2. [테스트 문제](#테스트-문제)
3. [성능 문제](#성능-문제)
4. [API 문제](#api-문제)
5. [디버깅 도구](#디버깅-도구)

---

## 구현 문제

### 깜빡임(Flicker) 현상

**증상**: 페이지 로드 시 원본 콘텐츠가 잠깐 보였다가 Target 콘텐츠로 교체됨.

**원인 및 해결**:

```yaml
원인 1: prehiding snippet 미적용
해결: head 태그 상단에 prehiding 추가
```

```html
<!-- 해결: prehiding snippet -->
<script>
  (function(d,s,a){
    a=d.documentElement;
    a.className+=' _prehide';
    setTimeout(function(){a.className=a.className.replace(/_prehide/,'')},3000);
  })(document);
</script>
<style>._prehide{opacity:0!important}</style>
```

```yaml
원인 2: at.js 비동기 로딩
해결: at.js를 동기 로딩하거나 bodyHidingEnabled 설정
```

```javascript
window.targetGlobalSettings = {
  bodyHidingEnabled: true,
  bodyHiddenStyle: "body {opacity: 0 !important}"
};
```

```yaml
원인 3: 콘텐츠 렌더링 지연
해결: 선택자 단순화, DOM 구조 최적화
```

### 경험이 적용되지 않음

**체크리스트**:

```yaml
1. 활동 상태 확인:
   - Target UI에서 활동이 "Live" 상태인지 확인
   - 시작/종료 날짜 확인

2. 대상자 조건 확인:
   - 방문자가 대상자 조건에 맞는지 확인
   - QA 링크로 강제 경험 확인

3. URL 규칙 확인:
   - VEC에서 설정한 URL과 실제 URL 일치 여부
   - 프로토콜(http/https) 확인
   - 쿼리 파라미터 영향 확인

4. mbox 확인:
   - mbox 이름 일치 여부
   - mbox가 실제로 호출되는지 확인
```

**디버깅 코드**:

```javascript
// at.js 디버그 모드 활성화
localStorage.setItem('mboxDebug', 'true');

// mbox 호출 확인
document.addEventListener('at-request-succeeded', function(e) {
  console.log('Target 요청 성공:', e.detail);
});

document.addEventListener('at-request-failed', function(e) {
  console.error('Target 요청 실패:', e.detail);
});
```

### 전환이 기록되지 않음

**체크리스트**:

```yaml
1. 목표 설정 확인:
   - 전환 mbox 이름 정확히 일치
   - 클릭 목표의 CSS 선택자 확인
   - 전환 페이지 URL 규칙 확인

2. 추적 코드 확인:
   - trackEvent 호출 여부
   - 주문 전환 시 필수 파라미터 확인

3. 세션 연속성 확인:
   - 동일 세션 내에서 전환 발생 여부
   - 크로스 도메인 추적 설정 확인
```

**전환 추적 디버깅**:

```javascript
// 주문 전환 필수 파라미터 확인
adobe.target.trackEvent({
  mbox: "orderConfirmPage",
  params: {
    "orderId": "ORD123",      // 필수: 중복 방지
    "orderTotal": "150000",   // 필수: 매출 추적
    "productPurchasedId": "SKU001,SKU002"  // 권장
  }
});

// 로깅 추가
console.log('Conversion tracked:', {
  orderId: orderId,
  orderTotal: orderTotal
});
```

---

## 테스트 문제

### 트래픽 불균등 배분

**증상**: 50/50 설정인데 실제 배분이 크게 다름.

**원인 및 해결**:

```yaml
원인 1: 샘플 크기 부족
해결: 최소 1,000 방문자 이상 확보 후 판단

원인 2: 대상자 조건 불일치
해결: 대상자 조건이 트래픽을 필터링하는지 확인

원인 3: 다른 활동과 충돌
해결: 활동 우선순위 및 충돌 그룹 확인
```

### 통계적 유의성 미달성

**체크리스트**:

```yaml
1. 충분한 전환 수:
   - 각 경험당 최소 50 전환 확보
   - Auto-Allocate는 최소 100 전환 권장

2. 적절한 테스트 기간:
   - 최소 1-2주 운영 (주간 패턴 반영)
   - 시즌/이벤트 기간 피하기

3. 효과 크기 검토:
   - 감지하려는 변화가 너무 작은지 검토
   - 더 큰 변화를 테스트하거나 트래픽 증가
```

**샘플 크기 계산**:

```javascript
// 샘플 크기 계산 함수
function calculateSampleSize(baselineRate, minimumDetectableEffect, power = 0.8, alpha = 0.05) {
  const zAlpha = 1.96;  // 95% 신뢰도
  const zBeta = 0.84;   // 80% 검정력

  const p1 = baselineRate;
  const p2 = baselineRate * (1 + minimumDetectableEffect);
  const pAvg = (p1 + p2) / 2;

  const n = 2 * Math.pow((zAlpha * Math.sqrt(2 * pAvg * (1 - pAvg)) +
                          zBeta * Math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))), 2) /
            Math.pow(p2 - p1, 2);

  return Math.ceil(n);
}

// 예시: 기본 전환율 5%, 20% 상대 개선 감지
console.log(calculateSampleSize(0.05, 0.20));
// 결과: 약 3,900 방문자/경험
```

### QA 모드 문제

**QA URL 생성**:

```yaml
URL 구조:
https://example.com?at_preview_token={token}&at_preview_index={experience_index}

파라미터:
- at_preview_token: Target UI에서 생성된 토큰
- at_preview_index: 경험 인덱스 (0부터 시작)
- at_preview_listed_activities_only: true/false
```

**QA 링크가 작동하지 않을 때**:

```yaml
1. 토큰 만료:
   - QA 링크는 기본 1일 후 만료
   - 새 QA 링크 생성

2. 브라우저 캐시:
   - 시크릿/프라이빗 모드로 테스트
   - 쿠키 및 캐시 삭제

3. URL 인코딩:
   - 특수 문자가 인코딩되었는지 확인

4. 대상자 조건:
   - QA에서도 대상자 조건 적용됨
   - 대상자 조건 일시적으로 제거하여 테스트
```

---

## 성능 문제

### 페이지 로드 지연

**진단**:

```javascript
// at.js 성능 측정
performance.measure('target-load', 'at-library-loaded', 'at-content-rendered');
const entries = performance.getEntriesByName('target-load');
console.log('Target 렌더링 시간:', entries[0].duration);
```

**최적화 방법**:

```yaml
1. 엣지 서버 활용:
   - CNAME 설정으로 자사 도메인 사용
   - CDN 캐싱 활성화

2. mbox 최적화:
   - 불필요한 mbox 제거
   - 배치 요청 활용 (getOffers)

3. 콘텐츠 최적화:
   - 오퍼 크기 최소화
   - 이미지 최적화
   - JSON 오퍼 활용
```

### 타임아웃 발생

**설정 조정**:

```javascript
window.targetGlobalSettings = {
  timeout: 5000,  // 기본 3000ms, 필요 시 증가
  selectorsPollingTimeout: 5000,  // 선택자 폴링 타임아웃
  bodyHidingEnabled: true,
  bodyHiddenStyle: "body {opacity: 0 !important}"
};
```

**타임아웃 처리**:

```javascript
adobe.target.getOffer({
  mbox: "hero-banner",
  timeout: 5000,
  success: function(offers) {
    adobe.target.applyOffers({ offers: offers });
  },
  error: function(status, error) {
    // 타임아웃 시 폴백 콘텐츠 표시
    if (status === 'timeout') {
      document.getElementById('hero').style.display = 'block';
      console.warn('Target timeout, showing default content');
    }
  }
});
```

---

## API 문제

### 401 Unauthorized

```yaml
원인:
- Access Token 만료 (24시간)
- JWT 서명 오류
- API Key 불일치

해결:
1. 새 Access Token 생성
2. Private Key 형식 확인 (PEM)
3. Technical Account ID 확인
```

### 403 Forbidden

```yaml
원인:
- API 권한 부족
- 워크스페이스 접근 권한 없음
- Property Token 누락

해결:
1. Admin Console에서 API 권한 확인
2. 올바른 워크스페이스 지정
3. Property Token 헤더 추가
```

### 429 Rate Limited

```javascript
// 지수 백오프 구현
async function apiCallWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);

      if (response.status === 429) {
        const delay = Math.pow(2, i) * 1000 + Math.random() * 1000;
        console.log(`Rate limited, retrying in ${delay}ms`);
        await new Promise(r => setTimeout(r, delay));
        continue;
      }

      return response;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
}
```

---

## 디버깅 도구

### Adobe Experience Platform Debugger

Chrome 확장 프로그램으로 실시간 Target 요청/응답 확인.

```yaml
확인 가능 항목:
- mbox 호출 및 응답
- 활동 및 경험 정보
- 프로필 파라미터
- Analytics 통합 데이터
```

### mboxDebug 모드

```javascript
// 콘솔 로그 활성화
localStorage.setItem('mboxDebug', 'true');

// 상세 로그
localStorage.setItem('mboxTrace', 'true');

// 비활성화
localStorage.removeItem('mboxDebug');
localStorage.removeItem('mboxTrace');
```

### Target Trace

```yaml
활성화 방법:
1. Target UI → 활동 → QA 모드
2. Authorization 헤더로 trace 요청

Trace 정보:
- 매칭된 활동 목록
- 대상자 평가 결과
- 경험 선택 이유
- 프로필 스크립트 실행 결과
```

### 네트워크 분석

```yaml
Chrome DevTools Network 탭:

검색 필터:
- mbox
- delivery
- tt.omtrdc.net

확인 항목:
- 요청 페이로드
- 응답 시간
- HTTP 상태 코드
- 응답 크기
```

### 로그 수집 스크립트

```javascript
// Target 이벤트 로깅
const targetEvents = [
  'at-library-loaded',
  'at-request-start',
  'at-request-succeeded',
  'at-request-failed',
  'at-content-rendering-start',
  'at-content-rendering-succeeded',
  'at-content-rendering-failed'
];

targetEvents.forEach(eventName => {
  document.addEventListener(eventName, function(e) {
    console.log(`[Target Event] ${eventName}:`, e.detail);
  });
});
```

### 일반적인 오류 코드

| 코드 | 의미 | 해결 |
|------|------|------|
| NO_CONTENT | 활동 없음 | 활동 상태/대상자 확인 |
| MBOX_NOT_FOUND | mbox 미존재 | mbox 이름 확인 |
| TIMEOUT | 응답 시간 초과 | 타임아웃 증가 또는 네트워크 확인 |
| INVALID_REQUEST | 잘못된 요청 | 파라미터 형식 확인 |
| UNAUTHORIZED | 인증 실패 | 토큰/API Key 확인 |
