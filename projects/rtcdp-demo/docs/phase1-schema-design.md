# Phase 1: XDM 스키마 설계

## 개요

AEP에 데이터를 수집하기 위해서는 먼저 XDM(Experience Data Model) 스키마를 정의해야 합니다. 이 가이드에서는 샘플 데이터에 맞는 4개의 스키마를 설계합니다.

---

## 스키마 구성 요소

### XDM 구조
```
Schema
├── Class (기본 구조)
│   ├── XDM Individual Profile (프로필 데이터)
│   └── XDM Experience Event (이벤트 데이터)
├── Field Groups (재사용 가능한 필드 집합)
│   ├── Standard Field Groups (Adobe 제공)
│   └── Custom Field Groups (직접 정의)
└── Data Types (복합 데이터 타입)
```

---

## Schema 1: Customer Profile Schema

### 기본 정보
- **이름**: `RTCDP Demo - Customer Profile`
- **클래스**: `XDM Individual Profile`
- **용도**: 고객 속성 데이터 저장

### 소스 데이터 (customer.csv)
```
customer_id, first_name, last_name, email, phone, city, country,
loyalty_points, join_date, membership_status
```

### Field Group 구성

#### 1. Demographic Details (Standard)
Adobe 제공 표준 필드 그룹
- `person.name.firstName`
- `person.name.lastName`

#### 2. Personal Contact Details (Standard)
- `personalEmail.address`
- `mobilePhone.number`

#### 3. RTCDP Demo - Customer Attributes (Custom)
**생성 필요**

| 필드 경로 | 타입 | 설명 |
|----------|------|------|
| `_rtcdpDemo.customerId` | String | 고객 고유 ID (Primary Identity) |
| `_rtcdpDemo.loyaltyPoints` | Integer | 적립 포인트 |
| `_rtcdpDemo.membershipStatus` | String (Enum) | Basic, Standard, Premium, VIP |
| `_rtcdpDemo.joinDate` | DateTime | 가입일 |
| `_rtcdpDemo.address.city` | String | 도시 |
| `_rtcdpDemo.address.country` | String | 국가 |

### Identity 설정
| 필드 | Identity Namespace | Type |
|------|-------------------|------|
| `_rtcdpDemo.customerId` | CustomerID | Primary |
| `personalEmail.address` | Email | Secondary |
| `mobilePhone.number` | Phone | Secondary |

### AEP UI 생성 단계

1. **Schemas > Create schema > XDM Individual Profile**
2. **Add field groups**:
   - Demographic Details
   - Personal Contact Details
3. **Create custom field group**:
   - Name: `RTCDP Demo - Customer Attributes`
   - Tenant namespace: `_rtcdpDemo`
4. **Set identities**:
   - `_rtcdpDemo.customerId` → Primary Identity (CustomerID namespace)
   - `personalEmail.address` → Identity (Email namespace)
5. **Enable for Profile**: Toggle ON

---

## Schema 2: Commerce Event Schema

### 기본 정보
- **이름**: `RTCDP Demo - Commerce Event`
- **클래스**: `XDM Experience Event`
- **용도**: 주문/구매 이벤트 저장

### 소스 데이터 (order.csv + order_item.csv)
```
order_id, customer_id, order_date, total_amount, status, payment_method
order_id, product_id, quantity, unit_price, total_price
```

### Field Group 구성

#### 1. Commerce Details (Standard)
- `commerce.order.purchaseID`
- `commerce.order.priceTotal`
- `commerce.purchases` (구매 이벤트 카운터)

#### 2. Product List Items (Standard)
- `productListItems[].SKU`
- `productListItems[].name`
- `productListItems[].quantity`
- `productListItems[].priceTotal`

#### 3. RTCDP Demo - Order Attributes (Custom)
**생성 필요**

| 필드 경로 | 타입 | 설명 |
|----------|------|------|
| `_rtcdpDemo.orderId` | String | 주문 고유 ID |
| `_rtcdpDemo.orderStatus` | String (Enum) | Processing, Shipped, Delivered, Completed |
| `_rtcdpDemo.paymentMethod` | String (Enum) | Credit Card, PayPal, Debit Card |
| `_rtcdpDemo.shippingAddress` | String | 배송 주소 |

### Identity 설정
| 필드 | Identity Namespace | Type |
|------|-------------------|------|
| `identityMap.CustomerID` | CustomerID | Primary |

### AEP UI 생성 단계

1. **Schemas > Create schema > XDM Experience Event**
2. **Add field groups**:
   - Commerce Details
   - Product List Items
3. **Create custom field group**:
   - Name: `RTCDP Demo - Order Attributes`
4. **Configure identityMap** for CustomerID
5. **Enable for Profile**: Toggle ON

---

## Schema 3: Web Event Schema

### 기본 정보
- **이름**: `RTCDP Demo - Web Event`
- **클래스**: `XDM Experience Event`
- **용도**: 웹 행동 이벤트 저장

### 소스 데이터 (sample-web-events.csv)
```
eventId, timestamp, personId, eventType, pageUrl, pageName,
referrerUrl, browser, device, browserWidth, browserHeight
```

### Field Group 구성

#### 1. Web Details (Standard)
- `web.webPageDetails.URL`
- `web.webPageDetails.name`
- `web.webReferrer.URL`

#### 2. Environment Details (Standard)
- `environment.browserDetails.userAgent`
- `environment.browserDetails.viewportWidth`
- `environment.browserDetails.viewportHeight`

#### 3. Device (Standard)
- `device.type`
- `device.model`

#### 4. RTCDP Demo - Web Event Attributes (Custom)
**생성 필요**

| 필드 경로 | 타입 | 설명 |
|----------|------|------|
| `_rtcdpDemo.eventId` | String | 이벤트 고유 ID |
| `_rtcdpDemo.eventType` | String (Enum) | page_view, add_to_cart, purchase |

### Identity 설정
| 필드 | Identity Namespace | Type |
|------|-------------------|------|
| `identityMap.ECID` | ECID | Primary |
| `identityMap.Email` | Email | Secondary (로그인 시) |

### AEP UI 생성 단계

1. **Schemas > Create schema > XDM Experience Event**
2. **Add field groups**:
   - Web Details
   - Environment Details
   - Device
3. **Create custom field group**:
   - Name: `RTCDP Demo - Web Event Attributes`
4. **Configure identityMap** for ECID and Email
5. **Enable for Profile**: Toggle ON

---

## Schema 4: Product Lookup Schema

### 기본 정보
- **이름**: `RTCDP Demo - Product Lookup`
- **클래스**: `Custom Lookup Class` (생성 필요)
- **용도**: 상품 정보 조회 (Lookup)

### 소스 데이터 (product.csv)
```
product_id, name, category, price, stock_quantity, description, brand
```

### Custom Class 생성

**Class Name**: `RTCDP Demo Product`
**Behavior**: Record (Lookup)

### Field 정의

| 필드 경로 | 타입 | 설명 |
|----------|------|------|
| `_rtcdpDemo.productId` | String | 상품 고유 ID (Primary Key) |
| `_rtcdpDemo.productName` | String | 상품명 |
| `_rtcdpDemo.category` | String | 카테고리 |
| `_rtcdpDemo.price` | Number | 가격 |
| `_rtcdpDemo.stockQuantity` | Integer | 재고 수량 |
| `_rtcdpDemo.description` | String | 상품 설명 |
| `_rtcdpDemo.brand` | String | 브랜드 |

### AEP UI 생성 단계

1. **Classes > Create class**:
   - Name: `RTCDP Demo Product`
   - Behavior: Record
2. **Schemas > Create schema** (사용자 정의 클래스 선택)
3. **Add fields** directly to schema
4. **Set `productId` as Primary Key**
5. **Create Dataset** for lookup

---

## 스키마 관계 (Relationships)

```
                    ┌─────────────────────┐
                    │  Customer Profile   │
                    │  (XDM Individual    │
                    │   Profile)          │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
   ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
   │  Commerce Event  │ │   Web Event      │ │ Product Lookup   │
   │  (Experience     │ │  (Experience     │ │ (Lookup Schema)  │
   │   Event)         │ │   Event)         │ │                  │
   └──────────────────┘ └──────────────────┘ └──────────────────┘
```

### 관계 설정

1. **Commerce Event → Customer Profile**
   - Reference: `identityMap.CustomerID`
   - Target: `_rtcdpDemo.customerId`

2. **Commerce Event → Product Lookup**
   - Reference: `productListItems[].SKU`
   - Target: `_rtcdpDemo.productId`

3. **Web Event → Customer Profile**
   - Reference: `identityMap.Email` (로그인 시)
   - Target: `personalEmail.address`

---

## 스키마 JSON 정의

각 스키마의 JSON 정의는 [schemas/](../schemas/) 폴더에서 확인할 수 있습니다.

- [profile-schema.json](../schemas/profile-schema.json)
- [commerce-event-schema.json](../schemas/commerce-event-schema.json)
- [web-event-schema.json](../schemas/web-event-schema.json)
- [product-lookup-schema.json](../schemas/product-lookup-schema.json)

---

## 완료 체크리스트

- [ ] Customer Profile Schema 생성 완료
- [ ] Commerce Event Schema 생성 완료
- [ ] Web Event Schema 생성 완료
- [ ] Product Lookup Schema 생성 완료
- [ ] 모든 Custom Field Group 생성 완료
- [ ] Primary Identity 설정 완료
- [ ] Profile 활성화 완료 (Profile, Commerce Event, Web Event)

---

## 다음 단계

스키마 설계가 완료되면 [Phase 2: Identity 설정](phase2-identity.md)으로 진행합니다.
