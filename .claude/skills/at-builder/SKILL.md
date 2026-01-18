---
name: at-builder
description: |
  Adobe Target 구현, A/B 테스트 설계 및 API 연동을 위한 종합 가이드.
  다음 작업에 사용: (1) at.js/Web SDK 구현 및 태그 설정, (2) A/B 테스트 및 다변량 테스트(MVT) 설계,
  (3) 오퍼/경험 생성 및 관리, (4) Recommendations 설정, (5) Adobe Target API 호출 및 자동화,
  (6) 테스트 결과 분석 및 인사이트 도출. 개인화, 전환율 최적화, 실험 설계가 필요할 때 활용.
---

# Adobe Target Builder 스킬

Adobe Target 구현부터 A/B 테스트 설계, API 자동화까지 전체 워크플로우 지원.

## 핵심 구성요소

### 활동(Activity) 유형

```
Adobe Target Activities
├── A/B Test - 두 개 이상의 경험 비교
├── Auto-Allocate - 자동 트래픽 최적화
├── Auto-Target - ML 기반 개인화
├── Experience Targeting (XT) - 규칙 기반 타겟팅
├── Multivariate Test (MVT) - 다중 요소 조합 테스트
├── Automated Personalization (AP) - 자동 개인화
└── Recommendations - 콘텐츠/제품 추천
```

### 활동 선택 가이드

| 목적 | 활동 유형 | 특징 |
|------|----------|------|
| 단순 A/B 비교 | A/B Test | 수동 트래픽 분배 |
| 빠른 승자 선정 | Auto-Allocate | 실시간 트래픽 최적화 |
| 개인화 추천 | Auto-Target | ML 기반 경험 선택 |
| 세그먼트별 경험 | Experience Targeting | 규칙 기반 타겟팅 |
| 복합 요소 테스트 | MVT | 여러 요소 조합 분석 |

## 빠른 시작

### at.js 기본 구현

```html
<!-- 1. at.js 로드 -->
<script src="https://assets.adobedtm.com/launch-{PROPERTY_ID}.min.js" async></script>

<!-- 2. 수동 구현 (자동 렌더링 비활성화 시) -->
<script>
adobe.target.getOffer({
  mbox: "target-global-mbox",
  success: function(offers) {
    adobe.target.applyOffers({ offers: offers });
  },
  error: function(status, error) {
    console.error("Target error:", error);
  }
});
</script>
```

### Web SDK 기본 구현

```javascript
// 초기화 (Target 활성화)
alloy("configure", {
  "edgeConfigId": "YOUR_DATASTREAM_ID",
  "orgId": "YOUR_ORG_ID@AdobeOrg"
});

// 개인화 요청
alloy("sendEvent", {
  "renderDecisions": true,
  "xdm": {
    "eventType": "decisioning.propositionDisplay"
  }
}).then(function(result) {
  console.log("Propositions:", result.propositions);
});
```

### 클릭 추적 이벤트

```javascript
// at.js 방식
adobe.target.trackEvent({
  mbox: "clicked-button",
  type: "click"
});

// Web SDK 방식
alloy("sendEvent", {
  "xdm": {
    "eventType": "decisioning.propositionInteract",
    "_experience": {
      "decisioning": {
        "propositions": [{
          "id": "PROPOSITION_ID",
          "scope": "button-click"
        }]
      }
    }
  }
});
```

## A/B 테스트 설계 워크플로우

1. **가설 정의**: 명확한 가설과 성공 지표 설정
2. **대상자 정의**: 세그먼트 또는 전체 방문자 선택
3. **경험 생성**: 대조군(Control) + 변형(Treatment) 설정
4. **트래픽 할당**: 각 경험별 트래픽 비율 설정
5. **목표 설정**: 전환, 클릭, 수익 등 KPI 지정
6. **QA 검증**: 미리보기 링크로 경험 검증
7. **활성화**: 테스트 시작 및 모니터링
8. **분석**: 통계적 유의성 달성 후 결과 해석

### 샘플 크기 계산

통계적 유의성을 위한 최소 샘플 크기:
- 기본 전환율 5%, 10% 상대 개선 감지 시 → 약 15,000 방문자/경험
- 기본 전환율 2%, 20% 상대 개선 감지 시 → 약 25,000 방문자/경험

```
필요 샘플 크기 = 16 × p(1-p) / (d × p)²
p = 기본 전환율
d = 감지하려는 상대적 개선폭
```

## 상세 가이드

작업 유형에 따라 아래 참조 문서 확인:

| 작업 | 참조 문서 |
|------|----------|
| at.js/Web SDK 구현 | [references/implementation.md](references/implementation.md) |
| A/B/MVT 테스트 설계 | [references/testing_guide.md](references/testing_guide.md) |
| Target API 연동 | [references/api_reference.md](references/api_reference.md) |
| 디버깅 및 문제 해결 | [references/troubleshooting.md](references/troubleshooting.md) |

## 대상자(Audience) 정의

### 기본 제공 속성

```
방문자 프로필
├── Geo (지역) - 국가, 도시, 위도/경도
├── Browser (브라우저) - 유형, 버전, 언어
├── Operating System - Windows, Mac, iOS, Android
├── Network - ISP, 연결 속도
├── Mobile - 디바이스, 화면 크기
├── Time Frame - 요일, 시간대
└── Traffic Sources - 참조 URL, 검색 엔진
```

### 커스텀 프로필 스크립트

```javascript
// 프로필 스크립트 예시: VIP 고객 판별
user.vipStatus = function() {
  return user.get("totalPurchases") > 500000 ? "VIP" : "Standard";
};
```

## 모범 사례

1. **한 번에 하나만 테스트** - 명확한 인과관계 파악
2. **충분한 트래픽 확보** - 통계적 유의성 달성까지 대기
3. **시즌 효과 고려** - 최소 1-2주 이상 테스트 운영
4. **깜빡임(Flicker) 방지** - 사전 숨김(prehiding) 적용
5. **QA 철저히 수행** - 모든 경험 미리보기 검증

## 공통 문제 해결

| 문제 | 원인 | 해결 |
|------|------|------|
| 깜빡임(Flicker) | 콘텐츠 교체 지연 | prehiding snippet 적용 |
| 경험 미적용 | mbox 미일치 | 페이지 URL 및 선택자 확인 |
| 전환 미집계 | 목표 설정 오류 | 전환 이벤트 및 mbox 검증 |
| 세그먼트 불일치 | 대상자 조건 오류 | 프로필 속성 값 확인 |

상세 문제 해결은 [references/troubleshooting.md](references/troubleshooting.md) 참조.