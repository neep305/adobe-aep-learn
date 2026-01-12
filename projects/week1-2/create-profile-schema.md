# 실습 1: 프로필 스키마 생성

## 목표
고객 프로필 정보를 저장할 수 있는 커스텀 스키마를 생성합니다.

## 단계별 가이드

### 1. AEP UI에서 스키마 생성

#### 스키마 기본 정보
1. Platform UI → Schemas 메뉴 접근
2. Create Schema → XDM Individual Profile 선택
3. 스키마 이름 지정: "Customer Profile Schema"

#### 필드 그룹 추가
다음 필드 그룹을 추가합니다:
- **Demographic Details**: 기본 인구통계 정보
- **Personal Contact Details**: 연락처 정보
- **Profile Person Details**: 개인 정보

### 2. API를 통한 스키마 생성 (선택)

Postman 또는 API 클라이언트를 사용하여 스키마를 생성할 수도 있습니다.

#### 요청 예시
```json
POST https://platform.adobe.io/data/foundation/schemaregistry/tenant/schemas
Headers:
  Authorization: Bearer {accessToken}
  Content-Type: application/json

Body:
{
  "title": "Customer Profile Schema",
  "description": "Customer profile information",
  "type": "object",
  "meta:extends": ["https://ns.adobe.com/xdm/context/profile"],
  "meta:abstract": false,
  "meta:extensible": false,
  "allOf": [
    {
      "$ref": "https://ns.adobe.com/xdm/context/profile"
    },
    {
      "properties": {
        "customerDetails": {
          "$ref": "https://ns.adobe.com/xdm/context/profile-person-details"
        }
      }
    }
  ]
}
```

### 3. Identity 필드 설정

1. 스키마 편집 모드로 진입
2. Primary Identity 필드 선택 (예: `personalEmail.address`)
3. Identity 네임스페이스 지정 (Email)
4. Save

### 4. 프로필 활성화

1. 스키마 메뉴에서 "Enable for Profile" 선택
2. 확인 대화상자에서 Enable 클릭

## 검증

생성된 스키마가 다음 조건을 만족하는지 확인:
- [ ] 스키마가 "Profile" 클래스를 사용
- [ ] Primary Identity가 설정됨
- [ ] 프로필 활성화 상태

## 다음 단계
- [이벤트 스키마 생성](./create-event-schema.md)

