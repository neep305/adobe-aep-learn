# 실습: Web SDK 구현

## 목표
간단한 웹페이지에 Adobe Experience Platform Web SDK를 구현합니다.

## 사전 준비
- AEP Web SDK 설정 (Edge Configuration ID 필요)
- Organizations ID 확인

## 1. HTML 페이지 생성

### 기본 HTML 파일 생성
`web-sdk-demo.html` 파일을 만듭니다:

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AEP Web SDK Demo</title>
</head>
<body>
    <h1>Adobe Experience Platform Web SDK Demo</h1>
    
    <div>
        <h2>이벤트 전송 테스트</h2>
        <button id="pageViewBtn">페이지뷰 이벤트 전송</button>
        <button id="customEventBtn">커스텀 이벤트 전송</button>
    </div>

    <div id="results"></div>

    <!-- AEP Web SDK -->
    <script src="https://cdn.jsdelivr.net/npm/@adobe/alloy@2.24.0/dist/alloy.min.js" async></script>
    
    <script>
        // SDK 초기화
        window.alloy("configure", {
            "edgeConfigId": "YOUR_EDGE_CONFIG_ID",
            "orgId": "YOUR_ORG_ID"
        });

        // 페이지뷰 이벤트
        document.getElementById("pageViewBtn").addEventListener("click", async () => {
            try {
                const result = await window.alloy("sendEvent", {
                    "xdm": {
                        "eventType": "web.webpagedetails.pageViews",
                        "web": {
                            "webPageDetails": {
                                "name": "Web SDK Demo Page",
                                "URL": window.location.href
                            }
                        }
                    }
                });
                document.getElementById("results").innerHTML = "<p>✅ 이벤트 전송 성공: " + JSON.stringify(result) + "</p>";
            } catch (error) {
                document.getElementById("results").innerHTML = "<p>❌ 오류: " + error.message + "</p>";
            }
        });

        // 커스텀 이벤트
        document.getElementById("customEventBtn").addEventListener("click", async () => {
            try {
                const result = await window.alloy("sendEvent", {
                    "xdm": {
                        "eventType": "web.custom.interaction",
                        "custom": {
                            "interactionType": "button_click",
                            "buttonName": "Custom Event Button"
                        }
                    }
                });
                document.getElementById("results").innerHTML = "<p>✅ 커스텀 이벤트 전송 성공: " + JSON.stringify(result) + "</p>";
            } catch (error) {
                document.getElementById("results").innerHTML = "<p>❌ 오류: " + error.message + "</p>";
            }
        });
    </script>
</body>
</html>
```

## 2. Edge Configuration 설정

### AEP UI에서 설정
1. Platform UI → Datastreams 메뉴 접근
2. New Datastream 생성
3. 이름 지정: "Web SDK Demo"
4. Event Schema 매핑 (이전에 생성한 이벤트 스키마)
5. Save

### Edge Configuration ID 확인
생성된 Datastream의 설정에서 Edge Configuration ID를 복사합니다.

## 3. 테스트 및 검증

### 로컬 웹 서버 실행
```bash
# Python을 사용한 간단한 서버
python3 -m http.server 8000

# 또는 Node.js http-server
npx http-server -p 8000
```

### 이벤트 확인
1. 브라우저에서 `http://localhost:8000/web-sdk-demo.html` 접속
2. 버튼 클릭하여 이벤트 전송
3. Adobe Experience Platform Debugger 사용하여 이벤트 확인
   - [Chrome Extension 설치](https://chrome.google.com/webstore/detail/adobe-experience-cloud-de/ocdmogmohccmeicdhlhhgeaonijenmgj)

### 데이터 확인
1. Platform UI → Datasets 메뉴
2. 해당 이벤트 스키마의 데이터셋 확인
3. 데이터 미리보기로 이벤트 확인

## 4. 고급 구현

### Identity 수집
```javascript
window.alloy("sendEvent", {
    "xdm": {
        "identityMap": {
            "email": [{
                "id": "user@example.com"
            }]
        }
    }
});
```

### 데이터 상호작용 추적
```javascript
// 장바구니 추가
window.alloy("sendEvent", {
    "xdm": {
        "eventType": "commerce.productListAdds",
        "commerce": {
            "productListAdds": {
                "value": 1
            }
        },
        "productListItems": [{
            "SKU": "PROD-123",
            "name": "Product Name",
            "priceTotal": 99.99
        }]
    }
});
```

## 검증 체크리스트
- [ ] HTML 페이지가 정상적으로 로드됨
- [ ] Edge Configuration ID가 올바르게 설정됨
- [ ] 이벤트가 Platform에 정상적으로 수집됨
- [ ] 데이터셋에서 이벤트 확인 가능
- [ ] Adobe Experience Platform Debugger로 이벤트 확인 가능

## 다음 단계
- [배치 수집 실습](./batch-ingestion.md)

