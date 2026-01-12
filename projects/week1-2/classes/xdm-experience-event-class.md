# XDM ExperienceEvent Class | Adobe Experience Platform

> Last update: September 25, 2025  
> Category: XDM Standard Class  
> Data behavior: Time-series (Event)

---

## 1. 개요 (Overview)

**XDM ExperienceEvent**는 Adobe Experience Platform의 표준 XDM 클래스 중 하나로,  
**특정 시점에 발생한 사건(event)에 대한 사실 기록(fact record)** 을 표현한다.

이 클래스는 “무엇이 언제 발생했는가”를 기록하기 위해 사용되며,  
고객 여정(Customer Journey)을 시간 순으로 재구성하는 데 핵심적인 역할을 한다.

ExperienceEvent는:
- 집계되지 않은(raw) 상태의 이벤트를 저장
- 해석이나 요약 없이 사실 그대로를 기록
- 명시적 이벤트와 암묵적 이벤트를 모두 포함

---

## 2. ExperienceEvent의 정의적 특징

### 2.1 이벤트의 의미
Experience Event는 다음을 포함한다:
- **발생 시점(timestamp)**
- **이벤트에 연관된 개인의 식별 정보**
- **발생한 행동 또는 상태 변화**

이벤트는 다음 두 가지 유형으로 나뉠 수 있다:
- **Explicit event**: 명확한 사용자 행동 (예: 클릭, 구매)
- **Implicit event**: 사용자 직접 행동 없이 발생 (예: 시스템 이벤트)

---

## 3. 데이터 모델 특성

### 3.1 데이터 행동 (Data Behavior)
- **Time-series**
- 각 레코드는 단일 이벤트를 나타냄
- 이벤트는 누적되며 수정되지 않는 것이 원칙

---

### 3.2 필수 시스템 필드
XDM ExperienceEvent 기반 스키마에는 다음 두 필드가 반드시 필요하다:

| 필드 | 설명 |
|---|---|
| `_id` | 이벤트 레코드를 고유하게 식별하는 ID |
| `timestamp` | 이벤트가 발생한 시점 (ISO 8601 / RFC 3339) |

---

## 4. 핵심 시스템 필드 상세

### 4.1 `_id` (Required)
- 이벤트 레코드 자체의 고유 식별자
- 이벤트 중복 방지 및 추적에 사용
- 개인(identity)을 식별하지는 않음
- UUID/GUID 또는 여러 필드 조합 후 해시(SHA-256 등) 생성 권장

> 동일한 `_id`를 가진 이벤트는 Profile Store에서는 중복 제거될 수 있으나,  
> Data Lake에는 그대로 저장될 수 있음

---

### 4.2 `timestamp` (Required)
- 이벤트가 **관측된 시점**
- 반드시 과거 시점이어야 함 (1970년 이후)
- 이벤트 자체의 시간만 표현해야 함

관련된 다른 시간 정보(예약 시작일 등)는:
- 클래스 레벨 timestamp가 아닌
- 별도의 필드로 모델링해야 함

---

### 4.3 기타 주요 필드

| 필드 | 설명 |
|---|---|
| `eventType` | 이벤트의 유형 또는 분류 |
| `producedBy` | 이벤트를 발생시킨 주체 |
| `identityMap` | 이벤트와 연관된 개인의 identity 집합 |
| `eventMergeId` | Web SDK 사용 시 자동 생성되는 배치 ID |

---

## 5. eventType 필드

- 이벤트의 성격을 나타내는 문자열
- 단일 이벤트 레코드에는 **하나의 eventType만 사용**
- 표준 값 + 사용자 정의 값 모두 허용 (extensible enum)

### eventType 사용 시 유의사항
- 하나의 hit에 여러 이벤트가 존재할 경우:
  - 계산 필드(calculated field)를 사용해 우선순위 결정
- 가장 중요한 이벤트를 대표하도록 설계 필요

---

## 6. Identity 처리 방식

- 개인 식별 정보는 `identityMap` 필드를 통해 관리
- identityMap은 시스템에 의해 자동 관리됨
- 수동으로 수정하는 것은 권장되지 않음

ExperienceEvent는:
- Profile과 연결되는 **행동 데이터의 입력 소스** 역할을 함

---

## 7. 이벤트 모델링 Best Practices

### 7.1 Timestamp 설계
- 클래스 레벨 timestamp는 **이벤트 관측 시점만** 표현
- 미래 시점의 의미 있는 날짜는 별도 필드 사용

---

### 7.2 Calculated Fields 활용
- 하나의 이벤트에 여러 의미가 포함될 경우:
  - Data Prep의 계산 필드를 사용해 대표 이벤트 도출
- 예:
  - page view + product view 동시 발생 → product view 우선

---

## 8. 호환 Field Groups (Compatible Field Groups)

Adobe는 ExperienceEvent에 대해 다양한 표준 Field Group을 제공한다. 예:

- Adobe Analytics ExperienceEvent Full Extension
- Advertising Details
- Commerce Details
- Campaign Marketing Details
- Web Details
- Media Analytics Interaction
- Reservation / Flight / Lodging 관련 Field Groups

Field Group 조합을 통해:
- 산업별 이벤트 모델링 가능
- 도메인 특화 이벤트 확장 가능

---

## 9. eventType 표준 값 (Appendix 요약)

eventType은 다음과 같은 범주를 포함한다:

- Advertising (impressions, clicks, completes 등)
- Commerce (productViews, addToCart, purchases 등)
- Web (pageViews, linkClicks, formFilledOut)
- Media (play, pause, adStart, sessionComplete 등)
- Direct Marketing (emailOpened, emailClicked 등)
- Decisioning (propositionDisplay, propositionInteract 등)
- Location (entry, exit)

---

## 10. producedBy 권장 값

| 값 | 의미 |
|---|---|
| `self` | 개인 또는 사용자가 직접 발생 |
| `system` | 시스템 자동 생성 |
| `salesRef` | 영업 담당자 |
| `customerRep` | 고객 응대 담당자 |

---

## 11. XDM Individual Profile과의 관계

| 구분 | Individual Profile | ExperienceEvent |
|---|---|---|
| 목적 | 개인의 상태 | 개인의 행동 |
| 데이터 성격 | Record | Time-series |
| 시간 의미 | 약함 | 핵심 |
| 예시 | 이메일, 선호도 | 클릭, 구매, 열람 |

ExperienceEvent는 Profile을 **행동 데이터로 강화**한다.

---

## 12. 핵심 요약

- XDM ExperienceEvent는 이벤트 중심 데이터 모델
- 시간(timestamp)이 가장 중요한 축
- 이벤트는 사실 그대로 기록
- `_id`와 `timestamp`는 필수
- IdentityMap을 통해 Profile과 연결
- Customer Journey Analytics 및 오케스트레이션의 핵심 기반

---
