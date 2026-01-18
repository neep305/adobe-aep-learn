# Adobe Analytics 디버깅 및 문제 해결

데이터 수집 검증, 일반적인 문제 해결, 디버깅 도구 활용 가이드.

## 목차

- [디버깅 도구](#디버깅-도구)
- [데이터 수집 검증](#데이터-수집-검증)
- [일반적인 문제와 해결](#일반적인-문제와-해결)
- [데이터 불일치 해결](#데이터-불일치-해결)
- [성능 문제 해결](#성능-문제-해결)

---

## 디버깅 도구

### Adobe Experience Platform Debugger

Chrome/Firefox 확장 프로그램으로 실시간 데이터 검증.

**설치:**
- [Chrome 웹 스토어](https://chrome.google.com/webstore/detail/adobe-experience-platform/bfnnokhpnncpkdmbokanobigaccjkpob)
- [Firefox Add-ons](https://addons.mozilla.org/firefox/addon/adobe-experience-platform-dbg/)

**주요 기능:**
1. **Summary**: 페이지에 로드된 Adobe 솔루션 개요
2. **Analytics**: AA 변수값 실시간 확인
3. **Network**: 비콘 요청 상세 정보
4. **Logs**: 실행 로그 및 에러

**Analytics 탭 확인 항목:**
```
Report Suite: 올바른 RSID 확인
Page Name: s.pageName 값
Variables: props, eVars, events 값
Products: s.products 문자열
```

### Charles Proxy / Fiddler

네트워크 레벨 비콘 캡처:

**Charles 필터 설정:**
```
*.2o7.net
*.omtrdc.net
*.demdex.net
```

**확인 항목:**
- 요청 URL 및 쿼리 파라미터
- 응답 상태 코드
- 요청/응답 헤더

### 브라우저 개발자 도구

**Network 탭:**
```
필터: b/ss (Analytics 비콘)
확인: 요청 URL의 쿼리 파라미터

예시 URL:
https://metrics.example.com/b/ss/rsid/0/JS-2.22.0/s12345?
  pageName=홈페이지&
  g=https://example.com&
  c1=카테고리A&
  v1=캠페인123&
  events=event1
```

**Console 탭:**
```javascript
// AppMeasurement 버전 확인
console.log(s.version);

// 현재 설정된 변수 확인
console.log(s.pageName);
console.log(s.eVar1);
console.log(s.events);

// 전체 비콘 문자열 확인 (전송 전)
console.log(s.t());
```

### Adobe Debugger (레거시)

북마클릿 방식 디버거:
```javascript
javascript:void(window.open("","stats_debugger","width=600,height=600,scrollbars=1").document.write("<script src=\"https://www.adobetag.com/d1/digitalpulsedebugger/live/DPD.js\"></"+"script>"));
```

---

## 데이터 수집 검증

### 체크리스트

**기본 설정:**
- [ ] Report Suite ID 정확성
- [ ] Tracking Server 설정
- [ ] Visitor ID Service 로드
- [ ] AppMeasurement/Web SDK 버전

**페이지뷰 트래킹:**
- [ ] s.pageName 설정 (필수)
- [ ] s.channel (사이트 섹션)
- [ ] s.server (호스트명)
- [ ] s.t() 단일 호출

**이벤트 트래킹:**
- [ ] s.events 문자열 형식
- [ ] s.products 구문 정확성
- [ ] s.purchaseID 중복 방지
- [ ] s.tl() 호출 확인

**변수 설정:**
- [ ] props 값 설정
- [ ] eVars 값 및 만료 설정
- [ ] 변수 초기화 (clearVars)

### 비콘 파라미터 해석

| 파라미터 | 변수 | 예시 |
|----------|------|------|
| pageName | s.pageName | 홈페이지 |
| g | 페이지 URL | https://example.com |
| r | referrer | https://google.com |
| c1-c75 | prop1-prop75 | 카테고리A |
| v1-v250 | eVar1-eVar250 | 캠페인123 |
| events | s.events | event1,purchase |
| products | s.products | ;SKU001;1;25000 |
| purchaseID | s.purchaseID | ORDER-123 |
| vid | Visitor ID | 12345-67890 |

### 테스트 시나리오

**1. 기본 페이지뷰:**
```
예상 결과:
- pageName 설정됨
- 단일 비콘 요청
- 200 응답
```

**2. 이커머스 구매:**
```
예상 결과:
- events=purchase
- products 문자열 포함
- purchaseID 설정
- 매출 값 정확
```

**3. 링크 트래킹:**
```
예상 결과:
- pe=lnk_o (커스텀 링크)
- pev2=링크명
- linkTrackVars에 설정된 변수만 포함
```

---

## 일반적인 문제와 해결

### 데이터 미수집

**증상:** 리포트에 데이터가 나타나지 않음

| 원인 | 진단 | 해결 |
|------|------|------|
| RSID 오류 | Debugger에서 RSID 확인 | 올바른 RSID로 수정 |
| Tracking Server 오류 | 네트워크 요청 실패 확인 | trackingServer 값 수정 |
| 비콘 차단 | AdBlocker 등 확인 | 1st party 서버 사용 |
| SSL 불일치 | HTTPS 페이지에서 HTTP 비콘 | trackingServerSecure 설정 |
| JS 에러 | Console 에러 확인 | 코드 수정 |

**진단 스크립트:**
```javascript
// Analytics 로드 확인
if (typeof s !== 'undefined') {
  console.log('✓ AppMeasurement 로드됨');
  console.log('RSID:', s.account);
  console.log('Tracking Server:', s.trackingServer);
} else {
  console.error('✗ AppMeasurement 미로드');
}
```

### 중복 페이지뷰

**증상:** 실제보다 2배의 페이지뷰 기록

| 원인 | 진단 | 해결 |
|------|------|------|
| s.t() 중복 호출 | Network 탭에서 비콘 수 확인 | 단일 호출로 수정 |
| SPA 라우팅 | 페이지 전환시 중복 확인 | 조건부 호출 추가 |
| 태그 매니저 중복 | 규칙 중복 실행 확인 | 규칙 조건 수정 |

**SPA 중복 방지:**
```javascript
// 이전 페이지와 다를 때만 전송
if (s.pageName !== previousPageName) {
  s.t();
  previousPageName = s.pageName;
}
```

### eVar 값 미적용

**증상:** eVar에 데이터가 수집되지 않음

| 원인 | 진단 | 해결 |
|------|------|------|
| 만료 설정 오류 | 관리자 > 변수 관리 확인 | 만료 기간 조정 |
| 값 미설정 | Debugger에서 값 확인 | 코드에서 값 설정 |
| 활성화 안됨 | 변수 관리에서 상태 확인 | 변수 활성화 |
| 머천다이징 설정 | 바인딩 이벤트 확인 | 적절한 이벤트와 함께 설정 |

### 구매 중복

**증상:** 동일 주문이 여러 번 기록

| 원인 | 진단 | 해결 |
|------|------|------|
| purchaseID 미설정 | Debugger에서 확인 | 고유 주문ID 설정 |
| 페이지 새로고침 | 사용자 행동 확인 | purchaseID 중복 체크 |
| 리다이렉트 | 확인 페이지 로직 확인 | 단일 전송 보장 |

**중복 방지 코드:**
```javascript
// 쿠키로 중복 체크
function trackPurchase(orderId) {
  var trackedOrders = getCookie('tracked_orders') || '';

  if (trackedOrders.indexOf(orderId) === -1) {
    s.events = 'purchase';
    s.purchaseID = orderId;
    s.t();

    setCookie('tracked_orders', trackedOrders + ',' + orderId, 30);
  }
}
```

### 이벤트 미기록

**증상:** 커스텀 이벤트가 리포트에 없음

| 원인 | 진단 | 해결 |
|------|------|------|
| 이벤트 비활성화 | 관리자 > 성공 이벤트 확인 | 이벤트 활성화 |
| 직렬화 중복 | 동일 serialization ID | 고유 ID 사용 |
| linkTrackEvents 미포함 | tl() 호출시 확인 | 이벤트 추가 |
| events 문자열 오류 | 구문 확인 | 올바른 형식 사용 |

**올바른 이벤트 형식:**
```javascript
// 단일 이벤트
s.events = 'event1';

// 복수 이벤트
s.events = 'event1,event2,event3';

// 수치 이벤트
s.events = 'event5=100';

// 직렬화 이벤트
s.events = 'event1:ABC123';

// 복합
s.events = 'event1,event5=100,purchase';
```

### products 변수 오류

**증상:** 상품 데이터 누락 또는 부정확

**올바른 형식:**
```javascript
// 기본 형식: 카테고리;상품;수량;가격
s.products = ';SKU001;1;25000';

// 복수 상품 (쉼표로 구분)
s.products = ';SKU001;1;25000,;SKU002;2;50000';

// 상품 레벨 이벤트
s.products = ';SKU001;1;25000;event10=500';

// 머천다이징 eVar
s.products = ';SKU001;1;25000;;eVar10=프로모션A';

// 전체 형식
s.products = '카테고리;SKU001;1;25000;event10=500;eVar10=프로모션A';
```

**일반적 오류:**
```javascript
// ❌ 쉼표 오류
s.products = ';SKU001;1;25000;;SKU002;2;50000';

// ✓ 올바른 구분
s.products = ';SKU001;1;25000,;SKU002;2;50000';

// ❌ 세미콜론 누락
s.products = 'SKU001;1;25000';

// ✓ 카테고리 자리 비워두기
s.products = ';SKU001;1;25000';
```

---

## 데이터 불일치 해결

### Analytics vs 다른 시스템

**일반적 불일치 원인:**

| 원인 | 설명 | 해결 |
|------|------|------|
| 측정 시점 | 클라이언트 vs 서버 | 데이터 정의 통일 |
| 필터링 | 봇 트래픽 제외 | 필터 설정 확인 |
| 시간대 | 타임존 차이 | 시간대 통일 |
| 세션 정의 | 30분 비활동 기준 | 정의 문서화 |
| 샘플링 | GA 등 샘플링 적용 | 샘플링 제거 |

### Report Suite 간 차이

**확인 사항:**
1. 보고서 세트 설정 비교
2. 처리 규칙 확인
3. 봇 규칙 설정
4. 내부 URL 필터

### 히스토리컬 데이터 변경

**영향 요소:**
- 분류 업데이트 (소급 적용)
- 처리 규칙 변경 (미래 데이터만)
- 마케팅 채널 규칙 변경

---

## 성능 문제 해결

### 페이지 로드 영향 최소화

**비동기 로딩:**
```html
<script src="AppMeasurement.js" async></script>
```

**지연 로딩:**
```javascript
// DOMContentLoaded 후 로드
document.addEventListener('DOMContentLoaded', function() {
  // Analytics 초기화
});
```

**Web Worker 사용 (고급):**
```javascript
// 무거운 처리는 Web Worker에서
const worker = new Worker('analytics-worker.js');
worker.postMessage({ type: 'track', data: analyticsData });
```

### 비콘 최적화

**불필요한 변수 제거:**
```javascript
// linkTrackVars로 필요한 변수만 전송
s.linkTrackVars = 'prop1,eVar1,events';
s.linkTrackEvents = 'event5';
s.tl(this, 'o', '클릭');
```

**배치 처리:**
```javascript
// 여러 이벤트를 단일 비콘으로
s.events = 'event1,event2,event3';
s.t();
```

### 디버깅 모드 비활성화

**프로덕션 환경:**
```javascript
// 개발 환경에서만 디버깅
if (location.hostname === 'dev.example.com') {
  s.debugTracking = true;
}
```

---

## 문제 해결 워크플로우

### 단계별 진단

```
1. 증상 확인
   └── 리포트에서 데이터 확인
   └── 예상 vs 실제 비교

2. 클라이언트 검증
   └── Debugger로 비콘 확인
   └── 변수값 정확성 검증
   └── 네트워크 요청 성공 확인

3. 서버 설정 확인
   └── 변수 활성화 상태
   └── 처리 규칙 확인
   └── 봇 필터 설정

4. 데이터 처리 확인
   └── 실시간 리포트 확인 (15분)
   └── 표준 리포트 확인 (2시간)
   └── Data Warehouse 확인 (24시간)

5. 해결 및 검증
   └── 수정 사항 적용
   └── 테스트 환경 검증
   └── 프로덕션 배포
   └── 데이터 확인
```

### 에스컬레이션 경로

```
Level 1: 자체 진단
- Debugger 확인
- 문서 참조
- 로그 분석

Level 2: 내부 전문가
- 구현 팀 확인
- 설정 검토

Level 3: Adobe 지원
- 케이스 생성
- 재현 단계 제공
- 스크린샷/로그 첨부
```
