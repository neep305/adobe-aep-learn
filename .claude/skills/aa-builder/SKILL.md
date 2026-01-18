---
name: adobe-analytics-builder
description: |
  Adobe Analytics 구현, 분석 및 API 연동을 위한 종합 가이드.
  다음 작업에 사용: (1) Web SDK/AppMeasurement 태그 구현, (2) Analysis Workspace 리포트 생성,
  (3) metrics/dimensions 데이터 분석, (4) Adobe Analytics API 2.0 호출 및 데이터 추출,
  (5) 이벤트 트래킹 설정, (6) eVar/prop/event 구성. 마케팅 분석, 사용자 행동 추적,
  전환 퍼널 분석이 필요할 때 활용.
---

# Adobe Analytics Builder 스킬

Adobe Analytics 구현부터 데이터 분석, API 연동까지 전체 워크플로우 지원.

## 핵심 구성요소

### 데이터 계층 구조

```
Report Suite (보고서 세트)
├── Dimensions (차원) - 데이터 분류 기준
│   ├── props (트래픽 변수) - 페이지 레벨
│   ├── eVars (전환 변수) - 방문자/방문 레벨
│   └── 기본 차원 - 페이지, 브라우저, 지역
├── Metrics (지표) - 수치 데이터
│   ├── events - 커스텀 성공 이벤트
│   └── 기본 지표 - 페이지뷰, 방문, 방문자
└── Segments (세그먼트) - 데이터 필터링
```

### props vs eVars

| 특성 | props | eVars |
|------|-------|-------|
| 지속성 | 히트 레벨만 | 설정 가능 (방문/방문자/고정) |
| 용도 | 페이지별 분석 | 전환 경로 분석 |
| 예시 | 검색어, 카테고리 | 캠페인 ID, 회원 등급 |

## 빠른 시작

### Web SDK 기본 구현

```javascript
// 초기화
alloy("configure", {
  "edgeConfigId": "YOUR_DATASTREAM_ID",
  "orgId": "YOUR_ORG_ID@AdobeOrg"
});

// 페이지뷰
alloy("sendEvent", {
  "xdm": {
    "eventType": "web.webpagedetails.pageViews",
    "web": { "webPageDetails": { "name": "홈페이지" } }
  }
});
```

### AppMeasurement 기본 구현

```javascript
var s = s_gi("YOUR_RSID");
s.trackingServer = "metrics.example.com";
s.pageName = "홈페이지";
s.prop1 = "카테고리A";
s.eVar1 = "캠페인123";
s.events = "event1";
s.t();
```

### 이커머스 이벤트

```javascript
// 구매 완료
s.events = "purchase";
s.products = ";SKU001;2;59000";
s.purchaseID = "ORDER123";  // 중복 방지 필수
s.t();
```

## 상세 가이드

작업 유형에 따라 아래 참조 문서 확인:

| 작업 | 참조 문서 |
|------|----------|
| 태그 구현 (Web SDK/AppMeasurement) | [references/implementation.md](references/implementation.md) |
| Analysis Workspace 리포트 | [references/workspace_reports.md](references/workspace_reports.md) |
| API 2.0 연동 | [references/api_reference.md](references/api_reference.md) |
| 디버깅 및 문제 해결 | [references/troubleshooting.md](references/troubleshooting.md) |

## 데이터 거버넌스

### PII 관리

- props/eVars에 개인식별정보 직접 저장 금지
- IP 난독화 설정 확인
- 쿠키 동의 관리 구현

### DULE 라벨

```
C1: 계약 데이터 - 내부 분석만 허용
C2: PII 포함 - 외부 공유 금지
I1: 직접 식별 가능 - 해시 처리 필요
```

## 모범 사례

1. **변수 명명 규칙 표준화** - SDR (Solution Design Reference) 문서 유지
2. **테스트 환경 분리** - 개발/스테이징/프로덕션 Report Suite 분리
3. **성능 최적화** - 비동기 로딩, 태그 매니저 활용

## 공통 문제 해결

| 문제 | 원인 | 해결 |
|------|------|------|
| 데이터 미수집 | Tracking Server 오류 | trackingServer 값 확인 |
| 중복 페이지뷰 | s.t() 중복 호출 | 단일 호출로 수정 |
| eVar 미적용 | 만료 설정 오류 | 관리자에서 만료 기간 확인 |
| 구매 중복 | purchaseID 미설정 | 고유 주문ID 설정 |

상세 문제 해결은 [references/troubleshooting.md](references/troubleshooting.md) 참조.
