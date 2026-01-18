# Adobe Target API 참조

## 목차

1. [인증](#인증)
2. [Admin API](#admin-api)
3. [Delivery API](#delivery-api)
4. [Recommendations API](#recommendations-api)
5. [공통 패턴](#공통-패턴)

---

## 인증

### JWT 인증 (Service Account)

```javascript
const jwt = require('jsonwebtoken');
const https = require('https');

// 1. JWT 생성
function createJWT(config) {
  const payload = {
    exp: Math.floor(Date.now() / 1000) + 60 * 60 * 24, // 24시간
    iss: config.orgId,
    sub: config.technicalAccountId,
    aud: `https://ims-na1.adobelogin.com/c/${config.apiKey}`,
    "https://ims-na1.adobelogin.com/s/ent_marketing_sdk": true
  };

  return jwt.sign(payload, config.privateKey, { algorithm: 'RS256' });
}

// 2. Access Token 교환
async function getAccessToken(jwtToken, config) {
  const params = new URLSearchParams({
    client_id: config.apiKey,
    client_secret: config.clientSecret,
    jwt_token: jwtToken
  });

  const response = await fetch('https://ims-na1.adobelogin.com/ims/exchange/jwt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString()
  });

  return response.json();
}
```

### OAuth 인증 (User Token)

```javascript
// OAuth 2.0 Authorization Code Flow
const authUrl = `https://ims-na1.adobelogin.com/ims/authorize?
  client_id=${CLIENT_ID}&
  redirect_uri=${REDIRECT_URI}&
  scope=openid,AdobeID,target_sdk&
  response_type=code`;

// Code를 Token으로 교환
async function exchangeCodeForToken(authCode) {
  const response = await fetch('https://ims-na1.adobelogin.com/ims/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      code: authCode
    })
  });

  return response.json();
}
```

### 공통 요청 헤더

```javascript
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'x-api-key': CLIENT_ID,
  'Content-Type': 'application/json',
  'Accept': 'application/vnd.adobe.target.v3+json'  // API 버전
};
```

---

## Admin API

### 활동(Activities) 관리

#### 활동 목록 조회

```bash
GET https://mc.adobe.io/{tenant}/target/activities
```

```javascript
// Node.js 예시
async function listActivities(accessToken, tenant) {
  const response = await fetch(
    `https://mc.adobe.io/${tenant}/target/activities?limit=50&offset=0`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'x-api-key': API_KEY,
        'Accept': 'application/vnd.adobe.target.v3+json'
      }
    }
  );

  return response.json();
}

// 응답 예시
{
  "total": 125,
  "offset": 0,
  "limit": 50,
  "activities": [
    {
      "id": 12345,
      "name": "홈페이지 A/B 테스트",
      "type": "ab",
      "state": "approved",
      "priority": 0,
      "modifiedAt": "2025-01-15T10:30:00Z"
    }
  ]
}
```

#### 활동 상세 조회

```bash
GET https://mc.adobe.io/{tenant}/target/activities/{activityId}
```

```javascript
async function getActivity(activityId) {
  const response = await fetch(
    `https://mc.adobe.io/${tenant}/target/activities/${activityId}`,
    { headers }
  );
  return response.json();
}
```

#### 활동 생성 (A/B 테스트)

```bash
POST https://mc.adobe.io/{tenant}/target/activities/ab
```

```javascript
const abTestPayload = {
  "name": "CTA 버튼 색상 테스트",
  "state": "saved",  // saved, approved, deactivated
  "priority": 0,
  "autoAllocateTraffic": {
    "enabled": false,
    "successEvaluationCriteria": "conversion_rate"
  },
  "locations": {
    "mboxes": [{
      "name": "cta-button-mbox",
      "audienceIds": [],
      "experienceLocalIds": [0, 1]
    }]
  },
  "experiences": [
    {
      "name": "Control",
      "localId": 0,
      "offerIds": [0]
    },
    {
      "name": "Orange Button",
      "localId": 1,
      "offerIds": [1]
    }
  ],
  "metrics": [{
    "name": "CTA Click",
    "metricLocalId": 0,
    "type": "click",
    "selector": "#cta-button"
  }],
  "reportingAudiences": [],
  "analytics": {
    "enabled": false
  }
};

async function createABTest(payload) {
  const response = await fetch(
    `https://mc.adobe.io/${tenant}/target/activities/ab`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    }
  );
  return response.json();
}
```

#### 활동 상태 변경

```bash
PUT https://mc.adobe.io/{tenant}/target/activities/{activityId}/state
```

```javascript
// 활동 활성화
await fetch(
  `https://mc.adobe.io/${tenant}/target/activities/${activityId}/state`,
  {
    method: 'PUT',
    headers,
    body: JSON.stringify({ state: "approved" })
  }
);

// 활동 비활성화
await fetch(
  `https://mc.adobe.io/${tenant}/target/activities/${activityId}/state`,
  {
    method: 'PUT',
    headers,
    body: JSON.stringify({ state: "deactivated" })
  }
);
```

### 대상자(Audiences) 관리

#### 대상자 목록 조회

```bash
GET https://mc.adobe.io/{tenant}/target/audiences
```

#### 대상자 생성

```javascript
const audiencePayload = {
  "name": "VIP 회원",
  "description": "총 구매액 100만원 이상 고객",
  "targetRule": {
    "and": [
      {
        "profile": {
          "parameter": "totalPurchase",
          "matcher": "greaterThanOrEquals",
          "values": [1000000]
        }
      }
    ]
  }
};

async function createAudience(payload) {
  const response = await fetch(
    `https://mc.adobe.io/${tenant}/target/audiences`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    }
  );
  return response.json();
}
```

### 오퍼(Offers) 관리

#### HTML 오퍼 생성

```javascript
const offerPayload = {
  "name": "Orange CTA Button",
  "content": `<button class="cta-btn" style="background-color: #FF6600;">지금 구매하기</button>`,
  "workspace": "default"
};

async function createHTMLOffer(payload) {
  const response = await fetch(
    `https://mc.adobe.io/${tenant}/target/offers/content`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    }
  );
  return response.json();
}
```

#### JSON 오퍼 생성

```javascript
const jsonOfferPayload = {
  "name": "Product Promo Data",
  "content": {
    "headline": "오늘만 30% 할인",
    "ctaText": "지금 쇼핑하기",
    "imageUrl": "https://example.com/promo.jpg"
  },
  "workspace": "default"
};

async function createJSONOffer(payload) {
  const response = await fetch(
    `https://mc.adobe.io/${tenant}/target/offers/json`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    }
  );
  return response.json();
}
```

---

## Delivery API

### 실시간 의사결정 요청

```bash
POST https://{clientCode}.tt.omtrdc.net/rest/v1/delivery
```

```javascript
const deliveryPayload = {
  "context": {
    "channel": "web",
    "browser": {
      "host": "example.com"
    },
    "address": {
      "url": "https://example.com/products"
    },
    "screen": {
      "width": 1920,
      "height": 1080
    },
    "userAgent": navigator.userAgent
  },
  "id": {
    "marketingCloudVisitorId": "12345678901234567890123456789012345678",
    "tntId": "abcdefg.28_0"  // 선택적
  },
  "property": {
    "token": "PROPERTY_TOKEN"  // 멀티 속성 사용 시
  },
  "execute": {
    "pageLoad": {},  // 글로벌 mbox
    "mboxes": [
      {
        "name": "hero-banner",
        "index": 0,
        "parameters": {
          "entity.id": "product123"
        },
        "profileParameters": {
          "memberTier": "gold"
        }
      }
    ]
  },
  "prefetch": {
    "views": []  // SPA 뷰 프리페치
  }
};

async function getOffers(clientCode, sessionId, payload) {
  const response = await fetch(
    `https://${clientCode}.tt.omtrdc.net/rest/v1/delivery?client=${clientCode}&sessionId=${sessionId}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'cache-control': 'no-cache'
      },
      body: JSON.stringify(payload)
    }
  );
  return response.json();
}

// 응답 예시
{
  "status": 200,
  "requestId": "abc123",
  "id": {
    "tntId": "abcdefg.28_0"
  },
  "execute": {
    "mboxes": [{
      "name": "hero-banner",
      "index": 0,
      "options": [{
        "type": "html",
        "content": "<div class='promo'>30% 할인</div>",
        "eventToken": "TOKEN_FOR_DISPLAY_NOTIFICATION"
      }],
      "analytics": {
        "payload": { "pe": "tnt", "tnta": "..." }
      }
    }]
  }
}
```

### 알림(Notification) 전송

```javascript
// 노출 알림
const notificationPayload = {
  "context": { /* 동일한 context */ },
  "id": { /* 동일한 id */ },
  "notifications": [{
    "id": "notification-1",
    "impressionId": "abc123",
    "timestamp": Date.now(),
    "type": "display",
    "mbox": {
      "name": "hero-banner"
    },
    "tokens": ["EVENT_TOKEN_FROM_DELIVERY_RESPONSE"]
  }]
};

// 클릭 알림
const clickNotification = {
  "notifications": [{
    "id": "click-1",
    "timestamp": Date.now(),
    "type": "click",
    "mbox": {
      "name": "hero-banner"
    },
    "tokens": ["EVENT_TOKEN"]
  }]
};
```

---

## Recommendations API

### 엔티티 업로드 (배치)

```bash
POST https://mc.adobe.io/{tenant}/target/recs/entities
```

```javascript
const entitiesPayload = {
  "entities": [
    {
      "id": "SKU001",
      "name": "프리미엄 헤드폰",
      "categoryId": "electronics,audio",
      "value": 299000,
      "inventory": 50,
      "thumbnailUrl": "https://example.com/sku001.jpg",
      "pageUrl": "https://example.com/products/sku001",
      "message": "베스트셀러",
      "custom1": "wireless",
      "custom2": "black"
    },
    {
      "id": "SKU002",
      "name": "블루투스 스피커",
      "categoryId": "electronics,audio",
      "value": 150000,
      "inventory": 100
    }
  ]
};

async function uploadEntities(payload) {
  const response = await fetch(
    `https://mc.adobe.io/${tenant}/target/recs/entities`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    }
  );
  return response.json();
}
```

### 컬렉션(Collection) 관리

```javascript
// 컬렉션 생성
const collectionPayload = {
  "name": "전자제품 베스트셀러",
  "rules": {
    "and": [
      { "categoryId": { "contains": "electronics" } },
      { "inventory": { "greaterThan": 0 } },
      { "value": { "greaterThan": 100000 } }
    ]
  }
};

async function createCollection(payload) {
  const response = await fetch(
    `https://mc.adobe.io/${tenant}/target/recs/collections`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    }
  );
  return response.json();
}
```

### 기준(Criteria) 생성

```javascript
const criteriaPayload = {
  "name": "최근 본 상품 기반 추천",
  "criteriaTitle": "고객님이 최근 본 상품",
  "type": "RECENTLY_VIEWED",
  "key": "entity.id",
  "daysCount": 30,
  "aggregation": "NONE"
};
```

---

## 공통 패턴

### 에러 처리

```javascript
async function targetAPICall(url, options) {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Target API Error: ${error.message || response.status}`);
    }

    return response.json();
  } catch (error) {
    if (error.message.includes('401')) {
      // 토큰 만료 - 재인증
      await refreshToken();
      return targetAPICall(url, options);
    }

    if (error.message.includes('429')) {
      // Rate Limit - 지수 백오프
      await sleep(Math.random() * 2000 + 1000);
      return targetAPICall(url, options);
    }

    throw error;
  }
}
```

### Rate Limits

| API | 제한 |
|-----|------|
| Admin API | 50 req/min |
| Delivery API | 50,000 req/sec |
| Recommendations 엔티티 | 1MB/요청 |

### 페이지네이션

```javascript
async function getAllActivities() {
  const allActivities = [];
  let offset = 0;
  const limit = 50;

  while (true) {
    const response = await fetch(
      `https://mc.adobe.io/${tenant}/target/activities?limit=${limit}&offset=${offset}`,
      { headers }
    );

    const data = await response.json();
    allActivities.push(...data.activities);

    if (allActivities.length >= data.total) break;
    offset += limit;
  }

  return allActivities;
}
```

### Postman Collection 설정

```json
{
  "environment": {
    "tenant": "{{YOUR_TENANT}}",
    "clientCode": "{{YOUR_CLIENT_CODE}}",
    "apiKey": "{{YOUR_API_KEY}}",
    "accessToken": "{{GENERATED_TOKEN}}",
    "orgId": "{{YOUR_ORG_ID}}@AdobeOrg"
  }
}
```
