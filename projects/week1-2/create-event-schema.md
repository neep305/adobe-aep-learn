# 실습 2: 이벤트 스키마 생성

## 목표
고객의 웹 활동을 추적할 수 있는 이벤트 스키마를 생성합니다.

## 단계별 가이드

### 1. 웹 페이지뷰 이벤트 스키마

#### 스키마 기본 정보
1. Platform UI → Schemas 메뉴 접근
2. Create Schema → XDM Experience Event 선택
3. 스키마 이름 지정: "Web Page View Event"

#### 필드 그룹 추가
다음 필드 그룹을 추가합니다:
- **Web Details**: 웹 브라우저 정보
- **Commerce Details**: 상거래 활동 정보 (선택)
- **Channel Information**: 채널 정보

### 2. API를 통한 스키마 생성 (선택)

```json
POST https://platform.adobe.io/data/foundation/schemaregistry/tenant/schemas
Headers:
  Authorization: Bearer {accessToken}
  Content-Type: application/json

Body:
{
  "title": "Web Page View Event",
  "description": "Web page view events",
  "type": "object",
  "meta:extends": ["https://ns.adobe.com/xdm/context/experienceevent"],
  "meta:abstract": false,
  "meta:extensible": false,
  "allOf": [
    {
      "$ref": "https://ns.adobe.com/xdm/context/experienceevent"
    },
    {
      "properties": {
        "web": {
          "$ref": "https://ns.adobe.com/xdm/context/webinfo"
        }
      }
    }
  ]
}
```

### 3. 필수 필드 확인

이벤트 스키마에는 다음 필드가 자동으로 포함됩니다:
- `timestamp`: 이벤트 발생 시간
- `eventType`: 이벤트 유형
- `endUserIDs`: 사용자 식별자

### 4. Identity 필드 설정

1. 스키마 편집 모드로 진입
2. 식별자 필드 선택 (예: `endUserIDs._experience.emailid` 또는 `_experience.analytics.customDimensions.eVars`)
3. Identity 네임스페이스 지정
4. Save

## 추가 실습: 커스텀 이벤트 유형

### 커스텀 필드 그룹 생성
다음과 같은 커스텀 필드 그룹을 만들어 특정 비즈니스 이벤트를 추적합니다:

```json
{
  "title": "Product Interaction Details",
  "description": "Product interaction tracking",
  "type": "object",
  "properties": {
    "productInteraction": {
      "type": "object",
      "properties": {
        "interactionType": {
          "type": "string",
          "title": "Interaction Type",
          "enum": ["view", "add_to_cart", "purchase", "review"]
        },
        "productId": {
          "type": "string",
          "title": "Product ID"
        },
        "productName": {
          "type": "string",
          "title": "Product Name"
        }
      }
    }
  }
}
```

## 검증

생성된 스키마가 다음 조건을 만족하는지 확인:
- [ ] 스키마가 "Experience Event" 클래스를 사용
- [ ] Identity 필드가 설정됨
- [ ] 웹 관련 필드가 포함됨

## 다음 단계
- [유니온 스키마 탐색](./explore-union-schema.md)

