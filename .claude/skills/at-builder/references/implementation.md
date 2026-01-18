# Adobe Target 구현 가이드

## 목차

1. [at.js 구현](#atjs-구현)
2. [Web SDK 구현](#web-sdk-구현)
3. [SPA 구현](#spa-구현)
4. [서버 사이드 구현](#서버-사이드-구현)
5. [깜빡임 방지](#깜빡임-방지)

---

## at.js 구현

### at.js 2.x 설치

```html
<!-- Adobe Launch를 통한 배포 (권장) -->
<script src="https://assets.adobedtm.com/launch-{PROPERTY_ID}.min.js" async></script>

<!-- 직접 배포 -->
<script src="at.js"></script>
```

### 기본 설정

```javascript
window.targetGlobalSettings = {
  clientCode: "YOUR_CLIENT_CODE",
  imsOrgId: "YOUR_ORG_ID@AdobeOrg",
  serverDomain: "YOUR_CLIENT_CODE.tt.omtrdc.net",
  timeout: 3000,
  globalMboxAutoCreate: true,
  bodyHidingEnabled: true,
  bodyHiddenStyle: "body {opacity: 0 !important}"
};
```

### getOffer / applyOffers

```javascript
// 단일 mbox
adobe.target.getOffer({
  mbox: "hero-banner",
  params: {
    "entity.id": "product123",
    "entity.categoryId": "electronics"
  },
  success: function(offers) {
    adobe.target.applyOffers({
      selector: "#hero-container",
      offers: offers
    });
  },
  error: function(status, error) {
    console.error("Target error:", status, error);
  }
});

// 여러 mbox 동시 요청
adobe.target.getOffers({
  request: {
    execute: {
      mboxes: [
        { name: "hero-banner", index: 0 },
        { name: "sidebar-promo", index: 1 }
      ]
    }
  }
}).then(function(response) {
  response.execute.mboxes.forEach(function(mbox) {
    adobe.target.applyOffers({
      selector: "#" + mbox.name,
      offers: mbox.options
    });
  });
});
```

### 전환 추적

```javascript
// 클릭 추적
document.getElementById("cta-button").addEventListener("click", function() {
  adobe.target.trackEvent({
    mbox: "cta-clicked",
    type: "click",
    params: {
      "productId": "SKU123"
    }
  });
});

// 페이지뷰 전환
adobe.target.trackEvent({
  mbox: "order-confirmation",
  type: "display",
  params: {
    "orderId": "ORD123",
    "orderTotal": 150000,
    "productPurchasedId": "SKU001,SKU002"
  }
});
```

---

## Web SDK 구현

### Alloy 설정

```javascript
alloy("configure", {
  "edgeConfigId": "YOUR_DATASTREAM_ID",
  "orgId": "YOUR_ORG_ID@AdobeOrg",
  "defaultConsent": "in",
  "debugEnabled": false,
  "prehidingStyle": "#hero, .promo-banner { opacity: 0 !important; }"
});
```

### 페이지 로드 시 개인화

```javascript
alloy("sendEvent", {
  "renderDecisions": true,
  "xdm": {
    "eventType": "decisioning.propositionDisplay",
    "web": {
      "webPageDetails": {
        "URL": window.location.href,
        "name": document.title
      }
    }
  },
  "decisionScopes": ["hero-banner", "sidebar-promo"]
}).then(function(result) {
  // 자동 렌더링된 proposition 확인
  console.log("Rendered:", result.propositions);
});
```

### 수동 렌더링

```javascript
alloy("sendEvent", {
  "renderDecisions": false,
  "decisionScopes": ["hero-banner"]
}).then(function(result) {
  const propositions = result.propositions || [];

  propositions.forEach(function(proposition) {
    proposition.items.forEach(function(item) {
      if (item.schema === "https://ns.adobe.com/personalization/html-content-item") {
        document.getElementById("hero-container").innerHTML = item.data.content;

        // 노출 알림 전송
        alloy("sendEvent", {
          "xdm": {
            "eventType": "decisioning.propositionDisplay",
            "_experience": {
              "decisioning": {
                "propositions": [{
                  "id": proposition.id,
                  "scope": proposition.scope
                }]
              }
            }
          }
        });
      }
    });
  });
});
```

### 전환 추적 (Web SDK)

```javascript
// 클릭 전환
alloy("sendEvent", {
  "xdm": {
    "eventType": "decisioning.propositionInteract",
    "_experience": {
      "decisioning": {
        "propositions": [{
          "id": "PROPOSITION_ID_FROM_RESPONSE",
          "scope": "hero-banner"
        }]
      }
    }
  }
});

// 주문 전환
alloy("sendEvent", {
  "xdm": {
    "eventType": "commerce.purchases",
    "commerce": {
      "order": {
        "purchaseID": "ORD123",
        "priceTotal": 150000
      },
      "purchases": { "value": 1 }
    },
    "productListItems": [
      { "SKU": "SKU001", "quantity": 1, "priceTotal": 100000 },
      { "SKU": "SKU002", "quantity": 2, "priceTotal": 50000 }
    ]
  }
});
```

---

## SPA 구현

### React 통합 (at.js)

```javascript
import { useEffect } from 'react';

function ProductPage({ productId }) {
  useEffect(() => {
    adobe.target.triggerView("product-" + productId);

    adobe.target.getOffer({
      mbox: "product-recommendations",
      params: { "entity.id": productId },
      success: function(offers) {
        adobe.target.applyOffers({ offers: offers });
      }
    });
  }, [productId]);

  return <div id="product-recommendations" />;
}
```

### React 통합 (Web SDK)

```javascript
import { useEffect } from 'react';

function ProductPage({ productId }) {
  useEffect(() => {
    window.alloy("sendEvent", {
      "renderDecisions": true,
      "xdm": {
        "web": {
          "webPageDetails": {
            "viewName": "product-" + productId
          }
        }
      },
      "decisionScopes": ["product-recommendations"]
    });
  }, [productId]);

  return <div id="product-recommendations" />;
}
```

### 뷰 변경 알림 (at.js)

```javascript
// SPA 라우트 변경 시
function onRouteChange(viewName) {
  adobe.target.triggerView(viewName, { page: false });
}

// React Router 예시
import { useLocation } from 'react-router-dom';

function App() {
  const location = useLocation();

  useEffect(() => {
    adobe.target.triggerView(location.pathname);
  }, [location]);
}
```

---

## 서버 사이드 구현

### Node.js Delivery API 호출

```javascript
const https = require('https');

async function getTargetOffers(visitorId, mboxName) {
  const payload = {
    context: {
      channel: "web",
      browser: { host: "example.com" },
      address: { url: "https://example.com/products" }
    },
    execute: {
      mboxes: [{
        name: mboxName,
        index: 0
      }]
    },
    id: {
      marketingCloudVisitorId: visitorId
    }
  };

  const options = {
    hostname: 'YOUR_CLIENT_CODE.tt.omtrdc.net',
    path: '/rest/v1/delivery?client=YOUR_CLIENT_CODE&sessionId=' + sessionId,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'cache-control': 'no-cache'
    }
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    });
    req.on('error', reject);
    req.write(JSON.stringify(payload));
    req.end();
  });
}
```

### Edge Decisioning (권장)

```javascript
// Adobe I/O Runtime 또는 서버리스 환경에서 사용
const { Core } = require('@adobe/aio-sdk');

async function getEdgeDecision(visitorId, scope) {
  const response = await fetch('https://edge.adobedc.net/ee/v2/interact', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': process.env.API_KEY
    },
    body: JSON.stringify({
      "event": {
        "xdm": {
          "identityMap": {
            "ECID": [{ "id": visitorId }]
          }
        }
      },
      "query": {
        "personalization": {
          "schemas": [
            "https://ns.adobe.com/personalization/html-content-item"
          ],
          "decisionScopes": [scope]
        }
      }
    })
  });

  return response.json();
}
```

---

## 깜빡임 방지

### Prehiding Snippet (at.js)

```html
<script>
  (function(w,d,s,l){
    w._prehideTargetElements=function(e){
      for(var t=e.length,n=0;n<t;n++)
        try{e[n].style.visibility="hidden"}catch(r){}
    };
    w._prehideTargetElements(d.querySelectorAll("body"));

    setTimeout(function(){
      w._prehideTargetElements=function(){};
      document.body.style.visibility="";
    }, 3000);
  })(window, document);
</script>
```

### 특정 요소만 숨기기

```javascript
window.targetGlobalSettings = {
  bodyHidingEnabled: false  // body 전체 숨기기 비활성화
};

// CSS로 특정 요소만 숨기기
<style>
  .personalized-content {
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  .personalized-content.at-element-marker {
    opacity: 1;
  }
</style>
```

### Web SDK Prehiding

```javascript
alloy("configure", {
  "prehidingStyle": `
    #hero-banner,
    .product-recommendations,
    [data-target-area] {
      opacity: 0 !important;
    }
  `
});
```

### 비동기 로딩 최적화

```html
<!-- at.js를 head에서 동기 로드 -->
<head>
  <style>
    body { opacity: 0 !important; }
  </style>
  <script src="at.js"></script>
  <script>
    // at.js 로드 완료 후 body 표시
    document.addEventListener("at-library-loaded", function() {
      document.body.style.opacity = "";
    });

    // 타임아웃 fallback
    setTimeout(function() {
      document.body.style.opacity = "";
    }, 3000);
  </script>
</head>
```
