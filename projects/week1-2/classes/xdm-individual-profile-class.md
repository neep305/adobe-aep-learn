# XDM Individual Profile Class | Adobe Experience Platform

> Last update: April 2, 2025  
> Category: XDM Standard Class  
> Data behavior: Record

---

## 1. 개요 (Overview)

**XDM Individual Profile**은 Adobe Experience Platform의 표준 XDM 클래스 중 하나로,  
**하나의 개인(person)에 대한 단일하고 통합된 표현(Profile)** 을 정의한다.

이 클래스는 브랜드와 상호작용한 개인에 대해 다음을 포괄적으로 표현한다:

- 완전히 식별된 사용자 (예: 이름, 이메일, 생년월일 보유)
- 부분적으로 식별된 사용자 (예: 쿠키, 디바이스 ID)
- 익명 사용자 (행동 신호만 존재)

XDM Individual Profile은 개인의 **속성(attributes)** 과 **관심사(interests)** 를 저장하는 데 초점을 둔다.

---

## 2. Profile의 개념적 범위

Individual Profile은 시간이 흐르며 누적되는 **개인 중심 데이터 저장소** 역할을 한다.

프로파일에는 다음 유형의 정보가 포함될 수 있다:

- 개인 정보 (이름, 생년월일, 위치)
- 식별자 정보 (이메일, 전화번호, 쿠키 ID 등)
- 연락처 정보
- 동의 및 선호 정보
- 멤버십 및 로열티 정보
- 세그먼트 소속 정보

> 행동 이벤트(클릭, 구매 등)는 이 클래스가 아니라 **XDM ExperienceEvent**에 저장된다.

---

## 3. 데이터 모델 특성

### 3.1 데이터 행동 (Data Behavior)
- **Record-based**
- 각 레코드는 특정 시점의 개인 상태를 나타냄
- 최신 상태가 중요하며, 시간 순 이벤트 추적 목적은 아님

---

### 3.2 Profile의 확장 방식
- Individual Profile 클래스는 단독으로 사용되지 않음
- **Compatible field group**을 통해 의미 있는 필드를 확장
- 필드 그룹 조합으로 조직별 프로파일 모델 구성

---

## 4. 핵심 시스템 필드 (Core Properties)

| 필드 | 설명 |
|---|---|
| `_id` | 레코드 자체를 식별하는 고유 ID (개인 ID 아님) |
| `_repo.createDate` | 레코드 최초 생성 시각 |
| `_repo.modifyDate` | 레코드 마지막 수정 시각 |
| `createdByBatchID` | 레코드를 생성한 배치 ID |
| `modifiedByBatchID` | 마지막 수정 배치 ID |
| `personID` | 개인을 식별하기 위한 내부 식별자 |
| `repositoryCreatedBy` | 레코드 생성 주체 |
| `repositoryLastModifiedBy` | 레코드 최종 수정 주체 |

### `_id` 필드에 대한 주의사항
- `_id`는 **개인(identity)** 이 아니라 **레코드(record)** 의 식별자
- UUID/GUID 또는 여러 필드를 조합 후 해시(SHA-256 등)하여 생성 권장
- 개인 식별 정보는 Identity field를 사용해야 함

---

## 5. Identity와의 관계

- 개인 식별 정보는 **Identity field**로 관리
- Identity field는 field group을 통해 정의됨
- 하나의 Profile에는 여러 identity가 매핑될 수 있음
  - 이메일
  - 전화번호
  - ECID
  - 기타 고객 ID

Identity는 프로파일 병합 및 통합의 핵심 요소이다.

---

## 6. 주요 호환 Field Groups (Compatible Field Groups)

Adobe에서 제공하는 대표적인 표준 Field Group은 다음과 같다:

- Consents and Preferences  
- Demographic Details  
- IdentityMap  
- Loyalty Details  
- Personal Contact Details  
- Segment Membership Details  
- Telecom Subscription  
- Work Contact Details  

### B2B 전용 Field Groups
(Real-Time CDP B2B Edition 필요)

- XDM Business Person Components  
- XDM Business Person Details  

> Field group 이름은 변경될 수 있으며, 최신 목록은 공식 문서 또는 GitHub 저장소 참조

---

## 7. Profile의 역할과 활용

XDM Individual Profile은 다음 기능의 기반이 된다:

- Real-Time Customer Profile
- 개인 단위 세그먼테이션
- 개인화 및 타겟팅
- 고객 여정 오케스트레이션
- 동의 및 선호도 관리

Profile은 **“누구인가(Who)”** 를 설명하고,  
Event는 **“무엇을 했는가(What happened)”** 를 설명한다.

---

## 8. 다른 XDM 클래스와의 관계

| 클래스 | 역할 |
|---|---|
| XDM Individual Profile | 개인의 상태 및 속성 |
| XDM ExperienceEvent | 개인의 행동 및 이벤트 |
| Relational Schema | 관계형 엔터티 모델링 |

Individual Profile은 ExperienceEvent와 함께 사용되어  
**속성 + 행동 기반 분석 및 활성화**를 가능하게 한다.

---

## 9. 설계 시 유의사항

- Profile에는 **변하지 않거나 비교적 느리게 변하는 데이터**를 저장
- 이벤트성 데이터 저장 지양
- Identity field 설계가 프로파일 품질에 결정적 영향
- 불필요한 필드 확장은 성능 및 거버넌스에 부담

---

## 10. 핵심 요약

- XDM Individual Profile은 개인 중심 데이터 모델
- Record 기반 스키마
- 행동이 아닌 상태(state)를 표현
- Identity 기반 프로파일 통합 지원
- 다양한 Field Group으로 확장 가능
- Real-Time CDP 및 개인화 기능의 핵심 기반

---
