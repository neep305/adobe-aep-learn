# Phase 3: 데이터 수집 (Data Ingestion)

## 개요

스키마와 Identity가 준비되면 실제 데이터를 AEP에 수집합니다. 이 가이드에서는 샘플 CSV 데이터를 XDM 형식으로 변환하고 Batch/Streaming 방식으로 수집하는 방법을 다룹니다.

---

## 데이터셋 생성

### 필요한 Dataset

| Dataset 이름 | 스키마 | 용도 |
|-------------|--------|------|
| RTCDP Demo - Customer Profiles | Customer Profile Schema | 고객 프로필 데이터 |
| RTCDP Demo - Commerce Events | Commerce Event Schema | 주문 이벤트 데이터 |
| RTCDP Demo - Web Events | Web Event Schema | 웹 행동 이벤트 |
| RTCDP Demo - Products | Product Lookup Schema | 상품 마스터 |

### AEP UI에서 Dataset 생성

1. **Datasets > Create dataset from schema**
2. 해당 스키마 선택
3. Dataset 이름 입력
4. **Enable for Profile** 체크 (Profile/Event 스키마만)

---

## 데이터 변환: CSV → XDM JSON

### 변환이 필요한 이유

- AEP는 XDM 형식의 JSON 데이터를 요구
- CSV 컬럼명을 XDM 필드 경로로 매핑
- 날짜/시간 형식을 ISO 8601로 변환

### 매핑 테이블

#### Customer Profile 매핑
| CSV 컬럼 | XDM 경로 |
|----------|----------|
| customer_id | `_rtcdpDemo.customerId` |
| first_name | `person.name.firstName` |
| last_name | `person.name.lastName` |
| email | `personalEmail.address` |
| phone | `mobilePhone.number` |
| city | `_rtcdpDemo.address.city` |
| country | `_rtcdpDemo.address.country` |
| loyalty_points | `_rtcdpDemo.loyaltyPoints` |
| join_date | `_rtcdpDemo.joinDate` |
| membership_status | `_rtcdpDemo.membershipStatus` |

#### Commerce Event 매핑
| CSV 컬럼 | XDM 경로 |
|----------|----------|
| order_id | `commerce.order.purchaseID` |
| customer_id | `identityMap.CustomerID[0].id` |
| order_date | `timestamp` |
| total_amount | `commerce.order.priceTotal` |
| status | `_rtcdpDemo.orderStatus` |
| payment_method | `_rtcdpDemo.paymentMethod` |
| product_id | `productListItems[].SKU` |
| quantity | `productListItems[].quantity` |
| unit_price | `productListItems[].priceTotal` |

---

## 변환 스크립트

### Python 스크립트 (csv-to-xdm.py)

```python
import csv
import json
from datetime import datetime

def convert_customer_to_xdm(csv_path):
    """customer.csv를 XDM JSON으로 변환"""
    records = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            xdm_record = {
                "person": {
                    "name": {
                        "firstName": row['first_name'],
                        "lastName": row['last_name']
                    }
                },
                "personalEmail": {
                    "address": row['email']
                },
                "mobilePhone": {
                    "number": row['phone']
                },
                "_rtcdpDemo": {
                    "customerId": row['customer_id'],
                    "loyaltyPoints": int(row['loyalty_points']),
                    "membershipStatus": row['membership_status'],
                    "joinDate": f"{row['join_date']}T00:00:00Z",
                    "address": {
                        "city": row['city'],
                        "country": row['country']
                    }
                }
            }
            records.append(xdm_record)

    return records

def convert_orders_to_xdm(orders_csv, items_csv):
    """order.csv + order_item.csv를 XDM JSON으로 변환"""
    # order_item을 order_id로 그룹핑
    items_by_order = {}
    with open(items_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            order_id = row['order_id']
            if order_id not in items_by_order:
                items_by_order[order_id] = []
            items_by_order[order_id].append({
                "SKU": row['product_id'],
                "quantity": int(row['quantity']),
                "priceTotal": float(row['total_price'])
            })

    # 주문 레코드 생성
    records = []
    with open(orders_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            order_id = row['order_id']
            xdm_record = {
                "timestamp": f"{row['order_date']}T00:00:00Z",
                "eventType": "commerce.purchases",
                "identityMap": {
                    "CustomerID": [{
                        "id": row['customer_id'],
                        "primary": True
                    }]
                },
                "commerce": {
                    "order": {
                        "purchaseID": order_id,
                        "priceTotal": float(row['total_amount'])
                    },
                    "purchases": {
                        "value": 1
                    }
                },
                "productListItems": items_by_order.get(order_id, []),
                "_rtcdpDemo": {
                    "orderId": order_id,
                    "orderStatus": row['status'],
                    "paymentMethod": row['payment_method']
                }
            }
            records.append(xdm_record)

    return records

def convert_web_events_to_xdm(csv_path):
    """sample-web-events.csv를 XDM JSON으로 변환"""
    records = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['eventId']:  # 빈 행 스킵
                continue
            xdm_record = {
                "timestamp": row['timestamp'],
                "eventType": f"web.{row['eventType']}",
                "identityMap": {
                    "ECID": [{
                        "id": row['personId'],
                        "primary": True
                    }]
                },
                "web": {
                    "webPageDetails": {
                        "URL": row['pageUrl'],
                        "name": row['pageName']
                    },
                    "webReferrer": {
                        "URL": row['referrerUrl'] if row['referrerUrl'] else None
                    }
                },
                "environment": {
                    "browserDetails": {
                        "viewportWidth": int(row['browserWidth']) if row['browserWidth'] else None,
                        "viewportHeight": int(row['browserHeight']) if row['browserHeight'] else None
                    }
                },
                "device": {
                    "type": row['device']
                },
                "_rtcdpDemo": {
                    "eventId": row['eventId'],
                    "eventType": row['eventType']
                }
            }
            records.append(xdm_record)

    return records

# 실행
if __name__ == "__main__":
    import os

    data_dir = "../../samples/data"
    output_dir = "../schemas"

    # Customer Profiles
    customers = convert_customer_to_xdm(f"{data_dir}/customer.csv")
    with open(f"{output_dir}/customer-data.json", 'w') as f:
        json.dump(customers, f, indent=2)
    print(f"Converted {len(customers)} customer records")

    # Commerce Events
    orders = convert_orders_to_xdm(
        f"{data_dir}/order.csv",
        f"{data_dir}/order_item.csv"
    )
    with open(f"{output_dir}/order-data.json", 'w') as f:
        json.dump(orders, f, indent=2)
    print(f"Converted {len(orders)} order records")

    # Web Events
    web_events = convert_web_events_to_xdm(f"{data_dir}/sample-web-events.csv")
    with open(f"{output_dir}/web-events-data.json", 'w') as f:
        json.dump(web_events, f, indent=2)
    print(f"Converted {len(web_events)} web event records")
```

---

## Batch Ingestion

### 방법 1: AEP UI 직접 업로드

1. **Datasets** > 해당 Dataset 선택
2. **Add data** 클릭
3. JSON 파일 업로드 (변환된 XDM JSON)
4. 수집 상태 확인

### 방법 2: Source Connector 사용

1. **Sources > Local file upload**
2. CSV 파일 선택
3. 스키마 매핑 UI에서 필드 매핑
4. 수집 실행

### 방법 3: API 사용

```bash
# 1. Batch 생성
curl -X POST 'https://platform.adobe.io/data/foundation/import/batches' \
  -H 'Authorization: Bearer {ACCESS_TOKEN}' \
  -H 'x-api-key: {API_KEY}' \
  -H 'x-gw-ims-org-id: {ORG_ID}' \
  -H 'x-sandbox-name: {SANDBOX_NAME}' \
  -H 'Content-Type: application/json' \
  -d '{
    "datasetId": "{DATASET_ID}",
    "inputFormat": {
      "format": "json"
    }
  }'

# 2. 파일 업로드
curl -X PUT 'https://platform.adobe.io/data/foundation/import/batches/{BATCH_ID}/datasets/{DATASET_ID}/files/{FILE_NAME}' \
  -H 'Authorization: Bearer {ACCESS_TOKEN}' \
  -H 'x-api-key: {API_KEY}' \
  -H 'x-gw-ims-org-id: {ORG_ID}' \
  -H 'Content-Type: application/octet-stream' \
  --data-binary @customer-data.json

# 3. Batch 완료 신호
curl -X POST 'https://platform.adobe.io/data/foundation/import/batches/{BATCH_ID}?action=COMPLETE' \
  -H 'Authorization: Bearer {ACCESS_TOKEN}' \
  -H 'x-api-key: {API_KEY}' \
  -H 'x-gw-ims-org-id: {ORG_ID}'
```

---

## Streaming Ingestion

### HTTP API Endpoint

```bash
curl -X POST 'https://dcs.adobedc.net/collection/{DATASTREAM_ID}' \
  -H 'Content-Type: application/json' \
  -d '{
    "header": {
      "schemaRef": {
        "id": "https://ns.adobe.com/{TENANT}/schemas/{SCHEMA_ID}",
        "contentType": "application/vnd.adobe.xed-full+json;version=1"
      },
      "datasetId": "{DATASET_ID}",
      "imsOrgId": "{ORG_ID}"
    },
    "body": {
      "xdmMeta": {
        "schemaRef": {
          "id": "https://ns.adobe.com/{TENANT}/schemas/{SCHEMA_ID}",
          "contentType": "application/vnd.adobe.xed-full+json;version=1"
        }
      },
      "xdmEntity": {
        "timestamp": "2023-10-15T10:30:00Z",
        "eventType": "web.webpagedetails.pageViews",
        "identityMap": {
          "ECID": [{"id": "12345", "primary": true}]
        },
        "web": {
          "webPageDetails": {
            "URL": "https://demo.example.com/product/123",
            "name": "Product Detail Page"
          }
        }
      }
    }
  }'
```

### Web SDK (실시간 수집)

```javascript
// Web SDK를 통한 이벤트 전송
alloy("sendEvent", {
  "xdm": {
    "eventType": "commerce.productViews",
    "commerce": {
      "productViews": {
        "value": 1
      }
    },
    "productListItems": [{
      "SKU": "PROD001",
      "name": "Wireless Headphones",
      "priceTotal": 199.99
    }]
  }
});
```

---

## 데이터 수집 순서

### 권장 수집 순서

1. **Product Lookup** (먼저)
   - 상품 마스터 데이터
   - 다른 데이터에서 참조

2. **Customer Profile**
   - 고객 속성 데이터
   - Identity Graph 기반 구축

3. **Commerce Events**
   - 구매 이력 데이터
   - CustomerID로 프로필 연결

4. **Web Events**
   - 웹 행동 데이터
   - ECID로 익명 추적

---

## 수집 검증

### 1. Dataset 모니터링

**Datasets > 해당 Dataset > Batches**
- Batch 상태: Success / Failed / Processing
- 레코드 수 확인
- 에러 로그 확인

### 2. Profile 확인

**Profiles > Browse**
- Identity Namespace 선택 (예: Email)
- 값 입력 (예: john.doe@example.com)
- 통합 프로필 확인

### 3. Query Service로 검증

```sql
-- 고객 프로필 확인
SELECT * FROM rtcdp_demo_customers LIMIT 10;

-- 주문 이벤트 확인
SELECT * FROM rtcdp_demo_commerce_events
ORDER BY timestamp DESC
LIMIT 10;

-- 고객별 주문 수
SELECT
  identityMap['CustomerID'][0].id as customer_id,
  COUNT(*) as order_count
FROM rtcdp_demo_commerce_events
GROUP BY 1
ORDER BY 2 DESC;
```

---

## 샘플 XDM 데이터

### Customer Profile 예시
```json
{
  "person": {
    "name": {
      "firstName": "John",
      "lastName": "Doe"
    }
  },
  "personalEmail": {
    "address": "john.doe@example.com"
  },
  "mobilePhone": {
    "number": "+1234567890"
  },
  "_rtcdpDemo": {
    "customerId": "CUST001",
    "loyaltyPoints": 1250,
    "membershipStatus": "Premium",
    "joinDate": "2022-01-15T00:00:00Z",
    "address": {
      "city": "New York",
      "country": "USA"
    }
  }
}
```

### Commerce Event 예시
```json
{
  "timestamp": "2023-10-01T00:00:00Z",
  "eventType": "commerce.purchases",
  "identityMap": {
    "CustomerID": [{
      "id": "CUST001",
      "primary": true
    }]
  },
  "commerce": {
    "order": {
      "purchaseID": "ORD001",
      "priceTotal": 299.98
    },
    "purchases": {
      "value": 1
    }
  },
  "productListItems": [
    {
      "SKU": "PROD001",
      "quantity": 1,
      "priceTotal": 199.99
    },
    {
      "SKU": "PROD004",
      "quantity": 1,
      "priceTotal": 29.99
    }
  ],
  "_rtcdpDemo": {
    "orderId": "ORD001",
    "orderStatus": "Completed",
    "paymentMethod": "Credit Card"
  }
}
```

---

## 완료 체크리스트

- [ ] Dataset 4개 생성 완료
- [ ] CSV → XDM JSON 변환 완료
- [ ] Product Lookup 데이터 수집 완료
- [ ] Customer Profile 데이터 수집 완료
- [ ] Commerce Events 데이터 수집 완료
- [ ] Web Events 데이터 수집 완료
- [ ] Profile에서 통합된 고객 확인
- [ ] Identity Graph 연결 확인

---

## 다음 단계

데이터 수집이 완료되면 [Phase 4: 세그먼트 정의](phase4-segmentation.md)로 진행합니다.
