# Relational Schemas | Adobe Experience Platform

> Last update: December 9, 2025  
> Availability: Limited (Journey Optimizer Orchestrated campaigns / 일부 CJA 라이선스)

---

## 1. 문서 개요 (Overview)

Relational schema는 Adobe Experience Platform(AEP) 데이터 레이크에서  
**정형 데이터(관계형 데이터)** 를 보다 명확하고 통제된 방식으로 모델링하기 위한 스키마 유형이다.

기존 XDM 스키마(Profile / ExperienceEvent / Lookup)와 달리,
- Union schema에 참여하지 않으며
- Field group 기반 자동 진화를 사용하지 않고
- **Primary key, 관계, 버전, 시간 식별자를 명시적으로 정의**한다.

목적은 다음과 같다:
- 관계형 데이터의 무결성 유지
- 조인 가능한 데이터 모델 제공
- 스키마 복잡도 및 예기치 않은 변경 방지

---

## 2. Standard XDM Schemas와의 차이점

### Standard XDM Schemas
- 데이터 행동 유형: Record / Time-series / Ad-hoc
- Union schema에 포함됨
- Field group 기반
- 자동 스키마 진화 발생
- 테넌트 네임스페이스 강제

### Relational Schemas
- Union schema에 **포함되지 않음**
- Field group **미사용**
- 필드를 직접 정의
- 스키마 진화 수동 관리
- Primary key, relationship을 명시적으로 선언
- 관계형 데이터 모델링에 특화

---

## 3. Relational Schemas의 주요 기능 (Features)

Relational schema는 다음 기능을 제공한다:

- **Primary key enforcement**
  - 단일 또는 복합 키 정의
  - 중복 데이터 방지

- **Change tracking**
  - Insert / Update / Delete 추적 가능

- **Schema-level relationships**
  - 스키마 메타 수준에서 관계 정의
  - 쿼리 시점에 동적 조인 가능

- **Union schema 회피**
  - 글로벌 스키마 변경의 영향 제거
  - 온보딩 단순화

- **정교한 데이터 모델링**
  - 애플리케이션별 데이터 모델 공존 가능

---

## 4. Required Descriptors (필수 메타데이터)

Relational schema는 데이터 행이 아니라  
**스키마 메타데이터(descriptor)** 를 통해 동작을 정의한다.

### 4.1 Primary Key Descriptor
- 각 레코드를 유일하게 식별
- 단일 필드 또는 복합 필드 가능

예시:
```json
{ "xdm:descriptor": "xdm:descriptorPrimaryKey", "xdm:sourceProperty": "orderId" }
