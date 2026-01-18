# Adobe Analytics 구현 가이드

Web SDK와 AppMeasurement를 사용한 Adobe Analytics 구현 상세 가이드.

## 목차

- [Web SDK 구현](#web-sdk-구현)
- [AppMeasurement 구현](#appmeasurement-구현)
- [이벤트 트래킹 패턴](#이벤트-트래킹-패턴)
- [데이터 레이어 설계](#데이터-레이어-설계)
- [태그 매니저 연동](#태그-매니저-연동)

---

## Web SDK 구현

### 초기 설정

```html
<!-- Web SDK 로드 -->
<script src="https://cdn1.adoberesources.net/alloy/2.19.0/alloy.min.js" async></script>
<script>
  alloy("configure", {
    "edgeConfigId": "YOUR_DATASTREAM_ID",
    "orgId": "YOUR_ORG_ID@AdobeOrg",
    "defaultConsent": "in",
    "edgeDomain": "data.example.com", // 선택: 1st party 도메인
    "idMigrationEnabled": true,       // 기존 ECID 마이그레이션
    "thirdPartyCookiesEnabled": true
  });
</script>
```

### 페이지뷰 트래킹

```javascript
alloy("sendEvent", {
  "xdm": {
    "eventType": "web.webpagedetails.pageViews",
    "web": {
      "webPageDetails": {
        "name": "상품 상세 페이지",
        "URL": window.location.href,
        "siteSection": "제품",
        "server": window.location.hostname
      },
      "webReferrer": {
        "URL": document.referrer
      }
    }
  }
});
```

### 커스텀 데이터 전송

```javascript
// XDM에 커스텀 필드 매핑
alloy("sendEvent", {
  "xdm": {
    "eventType": "web.webpagedetails.pageViews",
    "_example": {  // 스키마 tenant namespace
      "memberTier": "골드",
      "loginStatus": "로그인",
      "pageCategory": "전자제품"
    }
  },
  "data": {
    // Adobe Analytics 변수 직접 매핑 (데이터스트림 설정 필요)
    "__adobe": {
      "analytics": {
        "prop1": "카테고리A",
        "eVar1": "캠페인123",
        "events": "event1"
      }
    }
  }
});
```

### ID 동기화

```javascript
// 고객 ID 연결
alloy("setConsent", {
  consent: [{ standard: "Adobe", version: "2.0", value: { collect: { val: "y" } } }]
});

alloy("appendIdentityToUrl", {
  url: "https://partner.example.com"
}).then(result => {
  // result.url에 ECID가 포함된 URL 반환
});
```

---

## AppMeasurement 구현

### 기본 설정 (s_code.js)

```javascript
var s_account = "your_report_suite_id";
var s = s_gi(s_account);

// 필수 설정
s.trackingServer = "metrics.example.com";
s.trackingServerSecure = "smetrics.example.com";
s.visitorNamespace = "example";
s.visitor = Visitor.getInstance("YOUR_ORG_ID@AdobeOrg");

// 기본 변수
s.charSet = "UTF-8";
s.currencyCode = "KRW";
s.trackDownloadLinks = true;
s.trackExternalLinks = true;
s.trackInlineStats = true;
s.linkDownloadFileTypes = "exe,zip,wav,mp3,mov,mpg,avi,wmv,pdf,doc,docx,xls,xlsx,ppt,pptx";
s.linkInternalFilters = "javascript:,example.com";
s.linkLeaveQueryString = false;
s.linkTrackVars = "None";
s.linkTrackEvents = "None";
```

### 페이지뷰 트래킹

```javascript
// 페이지 정보 설정
s.pageName = "상품상세:전자제품:노트북A";
s.channel = "제품";
s.server = window.location.hostname;
s.pageType = ""; // 404 에러시 "errorPage"

// 계층 구조
s.hier1 = "홈|제품|전자제품|노트북";

// 트래픽 변수 (props)
s.prop1 = "전자제품";
s.prop2 = "노트북";
s.prop3 = new Date().getHours() + "시";

// 전환 변수 (eVars)
s.eVar1 = s.getQueryParam("cid"); // 캠페인 파라미터
s.eVar2 = "로그인";
s.eVar3 = "골드회원";

// 이벤트
s.events = "event1";

// 페이지뷰 전송
s.t();
```

### 링크 트래킹

```javascript
// 커스텀 링크 (이벤트 트래킹)
s.linkTrackVars = "prop1,eVar1,events";
s.linkTrackEvents = "event5";
s.prop1 = "CTA버튼";
s.eVar1 = "프로모션배너";
s.events = "event5";
s.tl(this, 'o', 'CTA클릭');

// 다운로드 링크
s.tl(this, 'd', 'PDF다운로드');

// 이탈 링크
s.tl(this, 'e', '외부사이트이동');
```

### 변수 초기화

```javascript
// 모든 변수 초기화 함수
function clearVars() {
  s.pageName = "";
  s.channel = "";
  s.prop1 = s.prop2 = s.prop3 = "";
  s.eVar1 = s.eVar2 = s.eVar3 = "";
  s.events = "";
  s.products = "";
}
```

---

## 이벤트 트래킹 패턴

### 이커머스 이벤트

```javascript
// 상품 조회
s.events = "prodView";
s.products = ";SKU001;;;;eVar10=상품카테고리";

// 장바구니 담기
s.events = "scAdd";
s.products = ";SKU001;1;25000";

// 장바구니 조회
s.events = "scView";
s.products = ";SKU001;1;25000,;SKU002;2;50000";

// 장바구니 제거
s.events = "scRemove";
s.products = ";SKU001;1;25000";

// 결제 시작
s.events = "scCheckout";
s.products = ";SKU001;1;25000,;SKU002;2;50000";

// 구매 완료
s.events = "purchase";
s.products = ";SKU001;1;25000;event10=2500,;SKU002;2;50000;event10=5000";
s.purchaseID = "ORDER-" + Date.now(); // 중복 제거용 필수
s.transactionID = "TXN123456";
```

### products 변수 구문

```
형식: 카테고리;상품명;수량;가격;이벤트;머천다이징eVar

예시:
";SKU001;1;25000"                           // 기본
"전자제품;SKU001;1;25000"                    // 카테고리 포함
";SKU001;1;25000;event10=2500"              // 상품 레벨 이벤트
";SKU001;1;25000;;eVar10=프로모션A"          // 머천다이징 eVar
";SKU001;1;25000;event10=2500;eVar10=할인"   // 전체
";SKU001;1;25000,;SKU002;2;50000"           // 복수 상품 (쉼표 구분)
```

### 커스텀 이벤트

```javascript
// 카운터 이벤트
s.events = "event1";  // 발생 횟수만 카운트

// 수치 이벤트
s.events = "event5=100";  // 100 값 전달 (예: 포인트)

// 통화 이벤트
s.events = "event10=49.99";  // 금액 (통화 설정 적용)

// 복수 이벤트
s.events = "event1,event5=100,scAdd";

// 이벤트 직렬화 (중복 제거)
s.events = "event1:ABC123";  // ABC123이 같으면 중복 제거
```

### 폼 트래킹

```javascript
// 폼 시작
document.getElementById('form').addEventListener('focus', function() {
  s.linkTrackVars = "events,eVar5";
  s.linkTrackEvents = "event20";
  s.events = "event20";
  s.eVar5 = "회원가입폼";
  s.tl(true, 'o', '폼시작');
}, { once: true });

// 폼 완료
document.getElementById('form').addEventListener('submit', function() {
  s.linkTrackVars = "events,eVar5";
  s.linkTrackEvents = "event21";
  s.events = "event21";
  s.eVar5 = "회원가입폼";
  s.tl(true, 'o', '폼완료');
});

// 폼 에러
function trackFormError(errorField, errorMessage) {
  s.linkTrackVars = "events,prop10,eVar10";
  s.linkTrackEvents = "event22";
  s.events = "event22";
  s.prop10 = errorField;
  s.eVar10 = errorMessage;
  s.tl(true, 'o', '폼에러');
}
```

### 비디오 트래킹

```javascript
// 비디오 시작
function trackVideoStart(videoName, videoDuration) {
  s.linkTrackVars = "events,eVar20,prop20";
  s.linkTrackEvents = "event30";
  s.events = "event30";
  s.eVar20 = videoName;
  s.prop20 = Math.floor(videoDuration) + "초";
  s.tl(true, 'o', '비디오시작');
}

// 비디오 완료
function trackVideoComplete(videoName) {
  s.linkTrackVars = "events,eVar20";
  s.linkTrackEvents = "event31";
  s.events = "event31";
  s.eVar20 = videoName;
  s.tl(true, 'o', '비디오완료');
}

// 비디오 진행률 (25%, 50%, 75%)
function trackVideoProgress(videoName, percent) {
  s.linkTrackVars = "events,eVar20,prop21";
  s.linkTrackEvents = "event32";
  s.events = "event32";
  s.eVar20 = videoName;
  s.prop21 = percent + "%";
  s.tl(true, 'o', '비디오진행:' + percent);
}
```

---

## 데이터 레이어 설계

### 표준 데이터 레이어 구조

```javascript
window.digitalData = {
  page: {
    pageInfo: {
      pageName: "홈페이지",
      pageURL: window.location.href,
      referrer: document.referrer,
      language: "ko-KR",
      siteSection: "홈"
    },
    category: {
      primaryCategory: "홈",
      subCategory1: "",
      pageType: "landing"
    }
  },
  user: {
    profile: {
      loginStatus: "비로그인",
      memberType: "",
      memberId: ""
    }
  },
  product: [],  // 상품 배열
  cart: {
    cartID: "",
    items: [],
    total: 0
  },
  transaction: {
    transactionID: "",
    total: 0,
    tax: 0,
    shipping: 0
  },
  event: []  // 이벤트 큐
};
```

### 데이터 레이어 활용

```javascript
// 데이터 레이어에서 변수 설정
function setAnalyticsFromDataLayer() {
  var dl = window.digitalData;

  // 페이지 정보
  s.pageName = dl.page.pageInfo.pageName;
  s.channel = dl.page.pageInfo.siteSection;
  s.prop1 = dl.page.category.primaryCategory;

  // 사용자 정보
  s.eVar1 = dl.user.profile.loginStatus;
  s.eVar2 = dl.user.profile.memberType;

  // 이벤트 처리
  if (dl.event && dl.event.length > 0) {
    var events = [];
    dl.event.forEach(function(e) {
      events.push(e.eventName);
    });
    s.events = events.join(',');
    dl.event = []; // 이벤트 큐 초기화
  }
}
```

---

## 태그 매니저 연동

### Adobe Launch 규칙 예시

```javascript
// 조건: Core - Page Bottom
// 작업: Adobe Analytics - Set Variables

// 데이터 요소 참조
%Data Layer - Page Name%
%Data Layer - Site Section%
%Data Layer - Login Status%

// 직접 코드 (Custom Code)
s.pageName = _satellite.getVar('pageName');
s.channel = _satellite.getVar('siteSection');
s.eVar1 = _satellite.getVar('loginStatus');
```

### Google Tag Manager 연동

```javascript
// GTM 데이터 레이어 이벤트
dataLayer.push({
  'event': 'productView',
  'ecommerce': {
    'detail': {
      'products': [{
        'name': '노트북A',
        'id': 'SKU001',
        'price': '1500000',
        'category': '전자제품/노트북'
      }]
    }
  }
});

// GTM에서 Adobe Analytics 태그로 매핑
// 변수: {{DL - Product Name}}, {{DL - Product ID}}
```

### 비동기 로딩 패턴

```html
<!-- 비동기 AppMeasurement 로딩 -->
<script>
(function() {
  var s = window.s || {};
  s.account = "your_rsid";

  // 설정 함수 큐
  s._q = s._q || [];
  s._q.push(['setAccount', s.account]);

  // 비동기 로드
  var script = document.createElement('script');
  script.src = '/path/to/AppMeasurement.js';
  script.async = true;
  document.head.appendChild(script);
})();
</script>
```
