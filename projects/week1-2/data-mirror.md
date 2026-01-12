# Data Mirror | Adobe Experience Platform

> Last update: December 9, 2025  
> Availability: Limited (Journey Optimizer Orchestrated campaigns / 일부 Customer Journey Analytics 라이선스)

---

## 1. Data Mirror 개요 (Overview)

Data Mirror는 Adobe Experience Platform(AEP)에서 제공하는 기능으로,  
**외부 데이터베이스의 변경 사항을 행(row) 단위로 AEP 데이터 레이크에 동기화**할 수 있도록 설계되었다.

이 기능은 기존 ETL(Extract, Transform, Load) 파이프라인 없이도 다음을 가능하게 한다:

- 삽입(Insert), 수정(Update), 삭제(Delete)의 정확한 반영
- 기존 관계형 데이터 모델 구조 유지
- 데이터 무결성 및 관계 보존

Data Mirror는 **Relational schema**를 기반으로 동작하며,  
데이터베이스의 구조를 AEP 내에서 그대로 “미러링”하는 것을 목표로 한다.

---

## 2. Data Mirror의 핵심 목적

Data Mirror의 주요 목적은 다음과 같다:

- 외부 데이터 웨어하우스와 AEP 데이터 레이크 간 **정합성 있는 동기화**
- 데이터 변경 이력(업데이트, 삭제 포함)의 정확한 반영
- 관계형 데이터 모델을 AEP 환경에서도 유지
- 복잡한 사전 ETL 프로세스 제거

즉, Data Mirror는 **“데이터베이스 → 데이터 레이크” 간의 구조 보존형 동기화**를 지향한다.

---

## 3. Capabilities and Benefits (주요 기능)

Data Mirror는 다음과 같은 기능을 제공한다.

### 3.1 Primary Key Enforcement
- 각 레코드를 고유하게 식별
- 중복 레코드 방지
- 단일 키 또는 복합 키 지원

---

### 3.2 Row-level Change Ingestion
- 레코드 단위의 변경 사항 처리
- Upsert 및 Delete 지원
- 전체 테이블 재적재 없이 변경분만 반영

---

### 3.3 Schema Relationships
- Relational schema의 descriptor를 사용하여 관계 정의
- Primary key / Foreign key 관계 보존
- 데이터 레벨이 아닌 **스키마 메타데이터 레벨**에서 관계 관리

---

### 3.4 Out-of-order Event Handling
- 데이터 변경이 순서대로 도착하지 않아도 처리 가능
- Version descriptor와 Timestamp descriptor를 활용해 최신 상태 판단

---

### 3.5 Direct Warehouse Integration
- 지원되는 클라우드 데이터 웨어하우스와 직접 연동
  - 예: Snowflake, Databricks, BigQuery
- Near real-time 수준의 변경 데이터 동기화 가능

---

## 4. Data Mirror가 해결하는 문제

Data Mirror는 다음과 같은 기존 문제를 해결한다:

- ETL 파이프라인 유지보수 비용
- 데이터 중복 및 정합성 문제
- 관계형 데이터의 평탄화(flattening)
- 삭제 데이터의 추적 불가
- 최신 상태 판단의 어려움

이를 통해 AEP는 **분석, 오케스트레이션, 컴플라이언스**에 적합한 데이터 상태를 유지할 수 있다.

---

## 5. Prerequisites (사전 요구 사항)

Data Mirror를 사용하기 전에 다음 사항을 이해하고 준비해야 한다.

- Experience Platform에서 스키마 생성(UI 또는 API)
- Cloud source 연결 구성
- Change Data Capture(CDC) 개념 이해
- Standard schema와 Relational schema의 차이 이해
- Descriptor 기반 관계 정의 방식 이해

---

## 6. Implementation Requirements (구현 요구사항)

Data Mirror를 사용하려면 다음 조건을 충족해야 한다.

### 6.1 Relational Schema 필수
- Data Mirror는 **Relational schema에서만 동작**
- Field group 사용 불가
- 필드를 직접 정의해야 함

---

### 6.2 필수 Descriptor
- Primary key descriptor (필수)
- Version descriptor (필수)
- Time-series schema인 경우 Timestamp descriptor 추가 필요

---

### 6.3 Source 시스템 요구사항
- Change Data Capture 지원 또는
- Insert / Update / Delete를 구분할 수 있는 메타데이터 제공
- Delete 감지를 위해 `_change_request_type` 컬럼 필요

---

## 7. Data Mirror 구현 흐름 (High-level Workflow)

### 7.1 스키마 정의
- Relational schema 생성
- Primary key, version, timestamp descriptor 정의

---

### 7.2 관계 매핑 및 데이터 관리
- Relationship descriptor로 데이터셋 간 관계 정의
- 데이터 품질 및 무결성 관리
- 삭제 시나리오 고려

---

### 7.3 Source 연결 구성
- Cloud source connection 설정
- 지원되는 ingestion 방식 선택

---

### 7.4 Change Data Capture 활성화
- CDC 기반 ingestion 설정
- 변경 데이터 자동 반영

---

## 8. Common Use Cases (대표 활용 사례)

### 8.1 Relational Data Modeling
- 기존 데이터베이스 구조를 그대로 AEP에 반영
- 관계형 데이터 모델 유지

---

### 8.2 Warehouse-to-Lake Synchronization
- 이벤트 로그, 트랜잭션 데이터 동기화
- 캠페인 및 오케스트레이션 활용 가능

---

### 8.3 Customer Journey Analytics Integration
- 이벤트 변경 이력 반영
- 정확한 트렌드 분석 및 행동 분석 지원

---

### 8.4 B2B Relationship Modeling
- Account–Contact–Subscription 구조 보존
- 리드 스코어링, 기회 관리에 활용

---

### 8.5 Subscription Management
- 갱신, 해지, 업그레이드, 다운그레이드 추적
- 전체 변경 이력 기반 분석

---

### 8.6 Data Hygiene Operations
- 규제 대응을 위한 정밀 삭제
- 데이터 정합성 유지

---

## 9. Important Considerations (중요 고려사항)

### 9.1 Data Deletion and Hygiene
- 삭제는 관계된 데이터셋 전체에 영향
- 설계 단계에서 삭제 시나리오 필수 검토

---

### 9.2 Schema Behavior Selection
- 기본값은 Record behavior
- 이벤트 추적이 필요하면 Time-series behavior 명시 필요

---

### 9.3 Ingestion Method Comparison
| 방식 | 용도 |
|---|---|
| Change Data Capture | 실시간/준실시간 동기화 |
| Data Distiller | SQL 기반 변환 및 적재 |
| File Upload | 배치 또는 수동 적재 |

---

### 9.4 Relationship Limitations
- One-to-one, Many-to-one만 지원
- Many-to-many 관계는 직접 지원하지 않음

---

## 10. Next Steps

Data Mirror 도입을 위해 다음 단계를 권장한다:

- 데이터 모델이 Primary key 및 변경 추적을 지원하는지 검토
- 라이선스 및 기능 활성화 여부 확인
- Relational schema 구조 사전 설계
- 적절한 ingestion 방식 선택

---

## 11. 핵심 요약

- Data Mirror는 **행 단위 변경 동기화 기능**
- Relational schema 기반으로 동작
- 관계형 데이터 모델을 AEP에 그대로 유지
- Upsert / Delete / Versioning 지원
- ETL 복잡성을 제거하고 데이터 정합성을 강화

---
