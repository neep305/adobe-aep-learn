# Week 1-2: AEP 아키텍처 및 핵심 개념

## 학습 목표
- XDM의 작동 원리와 스키마 설계 이해
- Identity Service의 ID 결합 메커니즘 파악
- Real-Time Customer Profile 아키텍처 이해

## 1. XDM (Experience Data Model)

### 개념
XDM은 Adobe Experience Platform의 데이터 표준화 프레임워크입니다. 모든 데이터를 일관된 구조로 정의하여 플랫폼 전반에서 재사용 가능하게 만듭니다.

### 주요 구성 요소

#### Schema (스키마)
데이터 구조의 청사진으로, 다음과 같이 구성됩니다:
- **Class**: 스키마의 기본 클래스 (예: XDM Individual Profile, XDM Experience Event)
- **Field Groups**: 재사용 가능한 필드 집합
- **Data Types**: 복잡한 데이터 구조 정의

#### Union Schema
여러 스키마에서 동일한 클래스를 사용하는 모든 필드를 자동으로 병합하여 생성되는 가상 스키마입니다.

### 실습 가이드
1. [프로필 스키마 생성](./projects/week1-2/create-profile-schema.md)
2. [이벤트 스키마 생성](./projects/week1-2/create-event-schema.md)
3. [유니온 스키마 탐색](./projects/week1-2/explore-union-schema.md)

## 2. Identity Service

### 개념
Identity Service는 서로 다른 시스템의 데이터를 단일 고객 프로필로 통합합니다.

### Identity Graph
고객의 모든 식별자(이메일, 전화번호, 쿠키 ID 등)를 연결하는 관계 네트워크입니다.

### Namespace (Identity Namespace)
식별자의 유형을 정의합니다:
- **ECID**: Adobe Experience Cloud ID
- **Email**: 이메일 주소
- **Phone**: 전화번호
- **Custom**: 커스텀 네임스페이스

### ID 결합 규칙
같은 네임스페이스 내의 값이 일치하면 동일한 identity로 간주됩니다.

### 실습 가이드
1. [Identity Namespace 생성](./projects/week1-2/create-identity-namespace.md)
2. [Identity Graph 탐색](./projects/week1-2/explore-identity-graph.md)

## 3. Real-Time Customer Profile

### 개념
고객의 모든 상호작용과 속성을 실시간으로 통합하여 단일 보기를 제공합니다.

### Profile vs Event 데이터

#### Profile 데이터
- 고객의 속성 정보 (이름, 이메일, 선호도 등)
- 시간에 따라 변경되는 정보
- XDM Individual Profile 클래스 사용

#### Event 데이터
- 고객의 행동 이벤트 (클릭, 구매, 방문 등)
- 특정 시점에 발생한 불변 이벤트
- XDM Experience Event 클래스 사용

### Merge Policy
여러 소스에서 동일한 필드의 값이 충돌할 때 어떤 값을 우선시할지 결정하는 정책입니다.

- **Timestamp Ordering**: 가장 최근 값 사용
- **Priority Ordering**: 데이터 소스 우선순위 기반
- **Data Governance Labels**: 거버넌스 레이블 기반 필터링

### Profile 저장소 구조
- **Profile Store**: 개별 프로필 데이터 저장
- **Profile Store (Standard)**: 표준 프로필 데이터
- **Profile Store (Edge)**: 실시간 엣지 프로필 데이터

### 실습 가이드
1. [Merge Policy 생성](./projects/week1-2/create-merge-policy.md)
2. [프로필 활성화](./projects/week1-2/enable-profile.md)
3. [프로필 탐색](./projects/week1-2/explore-profile.md)

## 학습 체크리스트

- [ ] XDM 스키마의 기본 구조 이해
- [ ] 스키마 클래스와 필드 그룹의 차이 설명 가능
- [ ] Identity Service의 작동 원리 설명 가능
- [ ] Profile과 Event 데이터의 차이 이해
- [ ] Merge Policy의 필요성과 작동 방식 이해
- [ ] 커스텀 스키마 3개 생성 완료
- [ ] Identity Graph에서 프로필 탐색 완료

## 참고 자료
- [XDM 개요](https://experienceleague.adobe.com/docs/experience-platform/xdm/home.html)
- [Identity Service 문서](https://experienceleague.adobe.com/docs/experience-platform/identity/home.html)
- [Real-Time Customer Profile 문서](https://experienceleague.adobe.com/docs/experience-platform/profile/home.html)

