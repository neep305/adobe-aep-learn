# Adobe Analytics API 2.0 레퍼런스

Adobe Analytics Reporting API 2.0을 사용한 데이터 추출 및 관리 가이드.

## 목차

- [인증 설정](#인증-설정)
- [API 엔드포인트](#api-엔드포인트)
- [리포트 API](#리포트-api)
- [세그먼트 API](#세그먼트-api)
- [계산된 지표 API](#계산된-지표-api)
- [분류 API](#분류-api)
- [에러 처리](#에러-처리)

---

## 인증 설정

### Adobe Developer Console 설정

1. [Adobe Developer Console](https://developer.adobe.com/console) 접속
2. 프로젝트 생성 → API 추가 → Adobe Analytics 선택
3. OAuth Server-to-Server 또는 Service Account (JWT) 선택
4. Product Profile에서 필요한 권한 부여

### OAuth Server-to-Server (권장)

```bash
# 액세스 토큰 발급
curl -X POST "https://ims-na1.adobelogin.com/ims/token/v3" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=openid,AdobeID,read_organizations,additional_info.projectedProductContext,additional_info.job_function"
```

### JWT 인증 (레거시)

```bash
# JWT 토큰 교환
curl -X POST "https://ims-na1.adobelogin.com/ims/exchange/jwt" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "jwt_token=YOUR_JWT_TOKEN"
```

### API 요청 헤더

```bash
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
-H "x-api-key: YOUR_API_KEY"
-H "x-proxy-global-company-id: YOUR_GLOBAL_COMPANY_ID"
-H "Content-Type: application/json"
```

---

## API 엔드포인트

### 기본 URL

```
https://analytics.adobe.io/api/{GLOBAL_COMPANY_ID}
```

### 주요 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | /reports/suites | 보고서 세트 목록 |
| POST | /reports | 리포트 데이터 조회 |
| GET | /segments | 세그먼트 목록 |
| POST | /segments | 세그먼트 생성 |
| GET | /calculatedmetrics | 계산된 지표 목록 |
| POST | /calculatedmetrics | 계산된 지표 생성 |
| GET | /dimensions | 차원 목록 |
| GET | /metrics | 지표 목록 |
| GET | /dateranges | 날짜 범위 목록 |
| GET | /users | 사용자 목록 |

---

## 리포트 API

### 기본 리포트 요청

```json
POST /reports
{
  "rsid": "your_report_suite_id",
  "globalFilters": [
    {
      "type": "dateRange",
      "dateRange": "2024-01-01T00:00:00.000/2024-01-31T23:59:59.999"
    }
  ],
  "metricContainer": {
    "metrics": [
      { "id": "metrics/visits", "columnId": "visits" },
      { "id": "metrics/pageviews", "columnId": "pageviews" },
      { "id": "metrics/visitors", "columnId": "visitors" }
    ]
  },
  "dimension": "variables/daterangeday",
  "settings": {
    "countRepeatInstances": true,
    "limit": 50,
    "page": 0
  }
}
```

### 다차원 분석 (Breakdown)

```json
{
  "rsid": "your_rsid",
  "globalFilters": [
    {
      "type": "dateRange",
      "dateRange": "2024-01-01T00:00:00.000/2024-01-31T23:59:59.999"
    }
  ],
  "metricContainer": {
    "metrics": [
      { "id": "metrics/visits" },
      { "id": "metrics/orders" },
      { "id": "metrics/revenue" }
    ]
  },
  "dimension": "variables/evar1",
  "metricsFilters": [
    {
      "dimension": "variables/page",
      "itemId": "1234567890"
    }
  ],
  "settings": {
    "limit": 10
  }
}
```

### 세그먼트 적용

```json
{
  "rsid": "your_rsid",
  "globalFilters": [
    {
      "type": "dateRange",
      "dateRange": "2024-01-01T00:00:00.000/2024-01-31T23:59:59.999"
    },
    {
      "type": "segment",
      "segmentId": "s300000000_1234567890"
    }
  ],
  "metricContainer": {
    "metrics": [
      { "id": "metrics/visits" }
    ],
    "metricFilters": [
      {
        "id": "filter1",
        "type": "segment",
        "segmentId": "s300000000_0987654321"
      }
    ]
  },
  "dimension": "variables/page"
}
```

### 검색 필터

```json
{
  "rsid": "your_rsid",
  "globalFilters": [
    {
      "type": "dateRange",
      "dateRange": "2024-01-01T00:00:00.000/2024-01-31T23:59:59.999"
    }
  ],
  "metricContainer": {
    "metrics": [{ "id": "metrics/pageviews" }]
  },
  "dimension": "variables/page",
  "search": {
    "clause": "CONTAINS 'product'",
    "excludeItemIds": ["0"],
    "includeSearchTotal": true
  },
  "settings": {
    "limit": 50
  }
}
```

### 날짜 비교 (이전 기간)

```json
{
  "rsid": "your_rsid",
  "globalFilters": [
    {
      "type": "dateRange",
      "dateRange": "2024-01-01T00:00:00.000/2024-01-31T23:59:59.999"
    }
  ],
  "metricContainer": {
    "metrics": [
      {
        "id": "metrics/visits",
        "columnId": "current_visits"
      },
      {
        "id": "metrics/visits",
        "columnId": "previous_visits",
        "filters": ["dateCompare"]
      }
    ],
    "metricFilters": [
      {
        "id": "dateCompare",
        "type": "dateRange",
        "dateRange": "2023-12-01T00:00:00.000/2023-12-31T23:59:59.999"
      }
    ]
  },
  "dimension": "variables/daterangeday"
}
```

### 응답 구조

```json
{
  "totalPages": 5,
  "firstPage": true,
  "lastPage": false,
  "numberOfElements": 50,
  "number": 0,
  "totalElements": 245,
  "columns": {
    "dimension": {
      "id": "variables/page",
      "type": "string"
    },
    "columnIds": ["visits", "pageviews", "visitors"]
  },
  "rows": [
    {
      "itemId": "1234567890",
      "value": "홈페이지",
      "data": [12500, 35000, 8500]
    },
    {
      "itemId": "1234567891",
      "value": "상품목록",
      "data": [8200, 22000, 5600]
    }
  ],
  "summaryData": {
    "totals": [125000, 350000, 85000],
    "col-max": [12500, 35000, 8500],
    "col-min": [100, 150, 50]
  }
}
```

---

## 세그먼트 API

### 세그먼트 목록 조회

```bash
GET /segments?rsids=your_rsid&limit=100&page=0&expansion=reportSuiteName,ownerFullName,modified,tags
```

### 세그먼트 상세 조회

```bash
GET /segments/{SEGMENT_ID}?expansion=definition,ownerFullName,modified,tags
```

### 세그먼트 생성

```json
POST /segments
{
  "name": "모바일 구매자",
  "description": "모바일 기기에서 구매한 사용자",
  "rsid": "your_rsid",
  "definition": {
    "container": {
      "func": "container",
      "context": "visitors",
      "pred": {
        "func": "and",
        "preds": [
          {
            "func": "streq",
            "str": "mobile",
            "val": {
              "func": "attr",
              "name": "variables/mobiledevicetype"
            }
          },
          {
            "func": "event",
            "name": "metrics/orders"
          }
        ]
      }
    }
  }
}
```

### 세그먼트 정의 연산자

```json
// 같음 (equals)
{ "func": "streq", "str": "값", "val": { "func": "attr", "name": "variables/evar1" } }

// 포함 (contains)
{ "func": "contains", "str": "검색어", "val": { "func": "attr", "name": "variables/page" } }

// 시작 (starts with)
{ "func": "streq-in", "list": ["시작값1", "시작값2"], "val": { "func": "attr", "name": "variables/page" } }

// 존재 (exists)
{ "func": "exists", "val": { "func": "attr", "name": "variables/evar5" } }

// 이벤트 발생
{ "func": "event", "name": "metrics/orders" }

// 수치 비교
{ "func": "ge", "num": 100, "val": { "func": "attr", "name": "variables/evar10" } }
```

### 세그먼트 컨테이너 레벨

```json
// 방문자 레벨
{ "func": "container", "context": "visitors", "pred": {...} }

// 방문 레벨
{ "func": "container", "context": "visits", "pred": {...} }

// 히트 레벨
{ "func": "container", "context": "hits", "pred": {...} }
```

---

## 계산된 지표 API

### 계산된 지표 목록

```bash
GET /calculatedmetrics?rsids=your_rsid&limit=100&expansion=definition,ownerFullName
```

### 계산된 지표 생성

```json
POST /calculatedmetrics
{
  "name": "전환율",
  "description": "주문 / 방문 * 100",
  "rsid": "your_rsid",
  "polarity": "positive",
  "precision": 2,
  "type": "percent",
  "definition": {
    "formula": {
      "func": "multiply",
      "col1": {
        "func": "divide",
        "col1": { "func": "metric", "name": "metrics/orders" },
        "col2": { "func": "metric", "name": "metrics/visits" }
      },
      "col2": 100
    }
  }
}
```

### 수식 함수

```json
// 나눗셈
{ "func": "divide", "col1": {...}, "col2": {...} }

// 곱셈
{ "func": "multiply", "col1": {...}, "col2": {...} }

// 덧셈
{ "func": "add", "col1": {...}, "col2": {...} }

// 뺄셈
{ "func": "subtract", "col1": {...}, "col2": {...} }

// 조건부 (IF)
{ "func": "if", "cond": {...}, "then": {...}, "else": {...} }

// 세그먼트 적용 지표
{
  "func": "calc-metric",
  "formula": { "func": "metric", "name": "metrics/orders" },
  "version": [1, 0, 0],
  "filters": [{ "func": "segment-ref", "id": "segment_id" }]
}
```

---

## 분류 API

### 분류 데이터 업로드

```json
POST /classifications/job
{
  "datasetId": "your_dataset_id",
  "jobName": "캠페인 분류 업데이트",
  "notifications": [
    { "method": "email", "recipients": ["user@example.com"] }
  ]
}
```

### 분류 파일 형식 (TSV)

```
## SC	your_rsid	evar1
Key	캠페인명	캠페인유형	시작일
CAMP001	신년프로모션	프로모션	2024-01-01
CAMP002	봄맞이이벤트	이벤트	2024-03-01
```

---

## 에러 처리

### HTTP 상태 코드

| 코드 | 의미 | 대응 |
|------|------|------|
| 200 | 성공 | - |
| 400 | 잘못된 요청 | 요청 본문 확인 |
| 401 | 인증 실패 | 토큰 갱신 |
| 403 | 권한 없음 | Product Profile 확인 |
| 404 | 리소스 없음 | ID 확인 |
| 429 | 속도 제한 | 재시도 (지수 백오프) |
| 500 | 서버 오류 | 재시도 |

### 에러 응답 예시

```json
{
  "errorCode": "invalid_token",
  "errorDescription": "The access token is invalid or has expired",
  "errorId": "abc123-def456"
}
```

### 속도 제한 처리

```python
import time
import requests

def api_request_with_retry(url, headers, payload, max_retries=5):
    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            wait_time = 2 ** attempt  # 지수 백오프
            time.sleep(wait_time)
        else:
            response.raise_for_status()

    raise Exception("Max retries exceeded")
```

### 페이지네이션 처리

```python
def get_all_pages(url, headers, payload):
    all_rows = []
    page = 0

    while True:
        payload["settings"]["page"] = page
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        all_rows.extend(data.get("rows", []))

        if data.get("lastPage", True):
            break
        page += 1

    return all_rows
```

---

## Python 클라이언트 예시

```python
import requests
import json

class AdobeAnalyticsClient:
    BASE_URL = "https://analytics.adobe.io/api"

    def __init__(self, client_id, client_secret, global_company_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.global_company_id = global_company_id
        self.access_token = None

    def authenticate(self):
        """OAuth 토큰 발급"""
        url = "https://ims-na1.adobelogin.com/ims/token/v3"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "openid,AdobeID,read_organizations,additional_info.projectedProductContext"
        }
        response = requests.post(url, data=data)
        self.access_token = response.json()["access_token"]

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": self.client_id,
            "x-proxy-global-company-id": self.global_company_id,
            "Content-Type": "application/json"
        }

    def get_report(self, rsid, metrics, dimension, date_range):
        """리포트 데이터 조회"""
        url = f"{self.BASE_URL}/{self.global_company_id}/reports"
        payload = {
            "rsid": rsid,
            "globalFilters": [
                {"type": "dateRange", "dateRange": date_range}
            ],
            "metricContainer": {
                "metrics": [{"id": m} for m in metrics]
            },
            "dimension": dimension,
            "settings": {"limit": 50}
        }
        response = requests.post(url, headers=self._headers(), json=payload)
        return response.json()

# 사용 예시
client = AdobeAnalyticsClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    global_company_id="YOUR_COMPANY_ID"
)
client.authenticate()

report = client.get_report(
    rsid="your_rsid",
    metrics=["metrics/visits", "metrics/pageviews"],
    dimension="variables/page",
    date_range="2024-01-01T00:00:00.000/2024-01-31T23:59:59.999"
)
print(json.dumps(report, indent=2, ensure_ascii=False))
```
