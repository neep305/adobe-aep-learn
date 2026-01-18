# Phase 5: 데모 웹사이트 (Web Demo)

## 개요

Adobe Web SDK(Alloy)가 통합된 샘플 이커머스 웹사이트를 구축합니다. 이 데모 사이트를 통해 실시간 이벤트 수집과 프로필 업데이트를 테스트할 수 있습니다.

---

## Web SDK 설정

### 1. Datastream 생성

**AEP UI에서 설정**:

1. **Data Collection > Datastreams > New Datastream**
2. 기본 정보:
   - Name: `RTCDP Demo Datastream`
   - Event Schema: `RTCDP Demo - Web Event`
3. Services 추가:
   - Adobe Experience Platform
     - Sandbox 선택
     - Event Dataset: `RTCDP Demo - Web Events`
     - Profile Dataset: `RTCDP Demo - Customer Profiles`
4. Datastream ID 복사

### 2. Tags (Launch) 설정 또는 직접 구현

이 가이드에서는 직접 Web SDK를 구현합니다.

---

## 데모 페이지 구조

```
web-demo/
├── index.html          # 홈페이지
├── product.html        # 상품 상세
├── cart.html           # 장바구니
├── checkout.html       # 결제
├── login.html          # 로그인
├── css/
│   └── style.css       # 스타일시트
└── js/
    └── analytics.js    # Web SDK 설정 및 이벤트
```

---

## Web SDK 기본 설정

### analytics.js

```javascript
// Web SDK 설정
(function() {
  // Alloy 라이브러리 로드
  !function(n,o){o.forEach(function(o){n[o]||((n.__alloyNS=n.__alloyNS||[]).push(o),
  n[o]=function(){var u=arguments;return new Promise(function(i,l){n[o].q.push([i,l,u])})},
  n[o].q=[])})}(window,["alloy"]);

  // 기본 설정
  alloy("configure", {
    "edgeConfigId": "YOUR_DATASTREAM_ID",  // Datastream ID로 교체
    "orgId": "YOUR_ORG_ID@AdobeOrg",        // IMS Org ID로 교체
    "defaultConsent": "in",
    "idMigrationEnabled": true,
    "thirdPartyCookiesEnabled": false,
    "debugEnabled": true  // 개발 중에만 true
  });
})();

// 페이지 뷰 이벤트
function trackPageView(pageName, pageUrl) {
  alloy("sendEvent", {
    "xdm": {
      "eventType": "web.webpagedetails.pageViews",
      "web": {
        "webPageDetails": {
          "name": pageName,
          "URL": pageUrl || window.location.href
        },
        "webReferrer": {
          "URL": document.referrer
        }
      }
    }
  });
}

// 상품 조회 이벤트
function trackProductView(product) {
  alloy("sendEvent", {
    "xdm": {
      "eventType": "commerce.productViews",
      "commerce": {
        "productViews": {
          "value": 1
        }
      },
      "productListItems": [{
        "SKU": product.sku,
        "name": product.name,
        "priceTotal": product.price,
        "quantity": 1
      }]
    }
  });
}

// 장바구니 추가 이벤트
function trackAddToCart(product, quantity) {
  alloy("sendEvent", {
    "xdm": {
      "eventType": "commerce.productListAdds",
      "commerce": {
        "productListAdds": {
          "value": 1
        }
      },
      "productListItems": [{
        "SKU": product.sku,
        "name": product.name,
        "priceTotal": product.price * quantity,
        "quantity": quantity
      }]
    }
  });
}

// 구매 완료 이벤트
function trackPurchase(order) {
  alloy("sendEvent", {
    "xdm": {
      "eventType": "commerce.purchases",
      "commerce": {
        "order": {
          "purchaseID": order.orderId,
          "priceTotal": order.total,
          "currencyCode": "USD"
        },
        "purchases": {
          "value": 1
        }
      },
      "productListItems": order.items.map(item => ({
        "SKU": item.sku,
        "name": item.name,
        "priceTotal": item.price * item.quantity,
        "quantity": item.quantity
      }))
    }
  });
}

// Identity 설정 (로그인 시)
function setCustomerIdentity(email, customerId) {
  alloy("setConsent", {
    "consent": [{
      "standard": "Adobe",
      "version": "1.0",
      "value": {
        "general": "in"
      }
    }]
  });

  alloy("sendEvent", {
    "xdm": {
      "eventType": "userLogin",
      "identityMap": {
        "Email": [{
          "id": email,
          "authenticatedState": "authenticated",
          "primary": false
        }],
        "CustomerID": [{
          "id": customerId,
          "authenticatedState": "authenticated",
          "primary": true
        }]
      }
    }
  });
}
```

---

## 페이지 구현

### index.html (홈페이지)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RTCDP Demo Store - Home</title>
  <link rel="stylesheet" href="css/style.css">

  <!-- Web SDK -->
  <script src="https://cdn1.adoberesources.net/alloy/2.19.0/alloy.min.js" async></script>
  <script src="js/analytics.js"></script>
</head>
<body>
  <header>
    <nav>
      <a href="index.html">Home</a>
      <a href="cart.html">Cart</a>
      <a href="login.html">Login</a>
    </nav>
  </header>

  <main>
    <h1>Welcome to RTCDP Demo Store</h1>

    <section class="products">
      <h2>Featured Products</h2>
      <div class="product-grid">
        <div class="product-card" data-sku="PROD001">
          <h3>Wireless Headphones</h3>
          <p class="price">$199.99</p>
          <a href="product.html?sku=PROD001">View Details</a>
        </div>
        <div class="product-card" data-sku="PROD002">
          <h3>Smartphone</h3>
          <p class="price">$899.99</p>
          <a href="product.html?sku=PROD002">View Details</a>
        </div>
        <div class="product-card" data-sku="PROD006">
          <h3>Laptop</h3>
          <p class="price">$1299.99</p>
          <a href="product.html?sku=PROD006">View Details</a>
        </div>
      </div>
    </section>
  </main>

  <script>
    // 페이지 뷰 트래킹
    document.addEventListener('DOMContentLoaded', function() {
      trackPageView('RTCDP Demo Store - Home');
    });
  </script>
</body>
</html>
```

### product.html (상품 상세)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Product Detail - RTCDP Demo Store</title>
  <link rel="stylesheet" href="css/style.css">
  <script src="https://cdn1.adoberesources.net/alloy/2.19.0/alloy.min.js" async></script>
  <script src="js/analytics.js"></script>
</head>
<body>
  <header>
    <nav>
      <a href="index.html">Home</a>
      <a href="cart.html">Cart</a>
      <a href="login.html">Login</a>
    </nav>
  </header>

  <main>
    <div id="product-detail">
      <h1 id="product-name">Loading...</h1>
      <p id="product-price"></p>
      <p id="product-description"></p>

      <div class="quantity-selector">
        <label for="quantity">Quantity:</label>
        <input type="number" id="quantity" value="1" min="1" max="10">
      </div>

      <button id="add-to-cart-btn">Add to Cart</button>
    </div>
  </main>

  <script>
    // 샘플 상품 데이터
    const products = {
      'PROD001': { sku: 'PROD001', name: 'Wireless Headphones', price: 199.99, description: 'High-quality wireless headphones' },
      'PROD002': { sku: 'PROD002', name: 'Smartphone', price: 899.99, description: 'Latest smartphone with advanced features' },
      'PROD006': { sku: 'PROD006', name: 'Laptop', price: 1299.99, description: 'Powerful laptop for work and gaming' }
    };

    // URL에서 SKU 파라미터 가져오기
    const urlParams = new URLSearchParams(window.location.search);
    const sku = urlParams.get('sku');
    const product = products[sku];

    if (product) {
      document.getElementById('product-name').textContent = product.name;
      document.getElementById('product-price').textContent = `$${product.price}`;
      document.getElementById('product-description').textContent = product.description;
      document.title = `${product.name} - RTCDP Demo Store`;

      // 페이지 뷰 + 상품 조회 트래킹
      document.addEventListener('DOMContentLoaded', function() {
        trackPageView(`Product: ${product.name}`);
        trackProductView(product);
      });

      // 장바구니 추가 버튼
      document.getElementById('add-to-cart-btn').addEventListener('click', function() {
        const quantity = parseInt(document.getElementById('quantity').value);
        trackAddToCart(product, quantity);

        // 로컬 스토리지에 장바구니 저장
        let cart = JSON.parse(localStorage.getItem('cart') || '[]');
        cart.push({ ...product, quantity });
        localStorage.setItem('cart', JSON.stringify(cart));

        alert('Added to cart!');
      });
    }
  </script>
</body>
</html>
```

### checkout.html (결제)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Checkout - RTCDP Demo Store</title>
  <link rel="stylesheet" href="css/style.css">
  <script src="https://cdn1.adoberesources.net/alloy/2.19.0/alloy.min.js" async></script>
  <script src="js/analytics.js"></script>
</head>
<body>
  <header>
    <nav>
      <a href="index.html">Home</a>
      <a href="cart.html">Cart</a>
    </nav>
  </header>

  <main>
    <h1>Checkout</h1>

    <div id="cart-summary">
      <!-- 장바구니 내용 -->
    </div>

    <form id="checkout-form">
      <h2>Billing Information</h2>
      <input type="email" id="email" placeholder="Email" required>
      <input type="text" id="name" placeholder="Full Name" required>

      <button type="submit">Complete Purchase</button>
    </form>
  </main>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      trackPageView('Checkout');

      // 장바구니 표시
      const cart = JSON.parse(localStorage.getItem('cart') || '[]');
      const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

      document.getElementById('cart-summary').innerHTML = `
        <h2>Order Summary</h2>
        <ul>
          ${cart.map(item => `<li>${item.name} x ${item.quantity} - $${(item.price * item.quantity).toFixed(2)}</li>`).join('')}
        </ul>
        <p><strong>Total: $${total.toFixed(2)}</strong></p>
      `;

      // 구매 완료 처리
      document.getElementById('checkout-form').addEventListener('submit', function(e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const orderId = 'ORD' + Date.now();

        // Identity 설정 (이메일 기반)
        setCustomerIdentity(email, null);

        // 구매 이벤트 전송
        trackPurchase({
          orderId: orderId,
          total: total,
          items: cart
        });

        // 장바구니 비우기
        localStorage.removeItem('cart');

        alert(`Order ${orderId} completed! Thank you for your purchase.`);
        window.location.href = 'index.html';
      });
    });
  </script>
</body>
</html>
```

### login.html (로그인)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Login - RTCDP Demo Store</title>
  <link rel="stylesheet" href="css/style.css">
  <script src="https://cdn1.adoberesources.net/alloy/2.19.0/alloy.min.js" async></script>
  <script src="js/analytics.js"></script>
</head>
<body>
  <header>
    <nav>
      <a href="index.html">Home</a>
      <a href="cart.html">Cart</a>
    </nav>
  </header>

  <main>
    <h1>Login</h1>

    <form id="login-form">
      <input type="email" id="login-email" placeholder="Email" required>
      <input type="text" id="customer-id" placeholder="Customer ID (e.g., CUST001)">
      <button type="submit">Login</button>
    </form>

    <div id="sample-accounts">
      <h3>Sample Accounts</h3>
      <ul>
        <li>john.doe@example.com (CUST001)</li>
        <li>jane.smith@example.com (CUST002)</li>
        <li>ivy.martinez@example.com (CUST010 - VIP)</li>
      </ul>
    </div>
  </main>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      trackPageView('Login');

      document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();

        const email = document.getElementById('login-email').value;
        const customerId = document.getElementById('customer-id').value;

        // Identity 설정
        setCustomerIdentity(email, customerId);

        localStorage.setItem('user', JSON.stringify({ email, customerId }));

        alert('Logged in successfully!');
        window.location.href = 'index.html';
      });
    });
  </script>
</body>
</html>
```

---

## 이벤트 검증

### AEP Debugger 사용

1. Chrome에서 [AEP Debugger](https://chrome.google.com/webstore/detail/adobe-experience-cloud-de/ocdmogmohccmeicdhlhhgeaonijenmgj) 설치
2. 데모 사이트 방문
3. Debugger 열기
4. **AEP Web SDK** 탭에서 이벤트 확인

### 확인해야 할 이벤트

| 페이지 | 이벤트 타입 | 확인 항목 |
|--------|-----------|----------|
| Home | pageViews | pageName, URL |
| Product | productViews | SKU, name, price |
| Add to Cart | productListAdds | SKU, quantity |
| Checkout | purchases | orderId, total, items |
| Login | userLogin | email, customerId |

### Console 디버깅

```javascript
// 브라우저 콘솔에서 디버그 모드 활성화
alloy("setDebug", {"enabled": true});
```

---

## 로컬 테스트 환경

### 간단한 HTTP 서버 실행

```bash
# Python 3
cd web-demo
python -m http.server 8000

# Node.js (http-server 설치 필요)
npx http-server web-demo -p 8000
```

### 테스트 URL
- Home: http://localhost:8000/index.html
- Product: http://localhost:8000/product.html?sku=PROD001
- Checkout: http://localhost:8000/checkout.html
- Login: http://localhost:8000/login.html

---

## 테스트 시나리오

### 시나리오 1: 익명 방문자
1. 홈페이지 방문 (ECID 생성)
2. 상품 조회
3. 장바구니 추가
4. 이탈 (Cart Abandoner 세그먼트)

### 시나리오 2: 로그인 사용자
1. 홈페이지 방문
2. 로그인 (john.doe@example.com)
3. 상품 조회
4. 구매 완료
5. Profile에서 Identity Graph 확인

### 시나리오 3: VIP 고객
1. VIP 계정으로 로그인 (ivy.martinez@example.com)
2. 상품 구매
3. VIP Customers 세그먼트 멤버십 확인

---

## 완료 체크리스트

- [ ] Datastream 생성 완료
- [ ] Web SDK 설정 완료 (edgeConfigId, orgId)
- [ ] index.html 페이지 완성
- [ ] product.html 페이지 완성
- [ ] checkout.html 페이지 완성
- [ ] login.html 페이지 완성
- [ ] 로컬 테스트 환경 구성
- [ ] AEP Debugger로 이벤트 검증
- [ ] AEP Profile에서 데이터 확인

---

## 다음 단계

데모 웹사이트가 완성되면 [Phase 6: Activation](phase6-activation.md)으로 진행합니다.
