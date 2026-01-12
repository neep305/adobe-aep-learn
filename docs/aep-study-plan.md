# Adobe Experience Platform 8주 학습 플랜

## 학습 플랜 개요

이 학습 플랜은 Adobe Experience Platform(AEP)의 핵심 개념부터 실무 활용까지 8주에 걸쳐 체계적으로 학습할 수 있도록 구성되었습니다. 각 주차별로 이론 학습과 실습 프로젝트를 병행하여 실무 역량을 키울 수 있습니다.

## 전체 학습 목표

- AEP의 핵심 아키텍처와 데이터 모델 이해
- 실시간 고객 프로필 구축 및 관리
- 다양한 채널을 통한 데이터 수집 구현
- 비즈니스 요구사항에 맞는 세그먼트 생성
- 외부 시스템으로의 데이터 활성화 및 통합

## 주차별 학습 계획

### Week 1-2: AEP 아키텍처 및 핵심 개념

**학습 목표**
- XDM의 작동 원리와 스키마 설계 이해
- Identity Service의 ID 결합 메커니즘 파악
- Real-Time Customer Profile 아키텍처 이해

**주요 학습 내용**

1. **XDM (Experience Data Model)**
   - Schema의 구조: Class, Field Groups, Data Types
   - XDM Individual Profile vs XDM Experience Event
   - Union Schema의 개념과 활용

2. **Identity Service**
   - Identity Graph의 작동 원리
   - Identity Namespace 설정 (ECID, Email, Phone, Custom)
   - ID 결합 규칙 및 프라이빗 그래프

3. **Real-Time Customer Profile**
   - Profile 데이터 vs Event 데이터의 차이
   - Merge Policy (Timestamp Ordering, Priority Ordering)
   - Profile Store 구조

**실습 프로젝트**
- [ ] 프로필 스키마 생성 (고객 정보)
- [ ] 이벤트 스키마 생성 (웹 행동 데이터)
- [ ] Identity Namespace 생성
- [ ] Merge Policy 설정
- [ ] Union Schema 탐색

**학습 체크리스트**
- [ ] XDM 스키마의 기본 구조 이해
- [ ] 스키마 클래스와 필드 그룹의 차이 설명 가능
- [ ] Identity Service의 작동 원리 설명 가능
- [ ] Profile과 Event 데이터의 차이 이해
- [ ] Merge Policy의 필요성과 작동 방식 이해
- [ ] 커스텀 스키마 3개 생성 완료
- [ ] Identity Graph에서 프로필 탐색 완료

**참고 문서**: [docs/week1-2-architecture.md](docs/week1-2-architecture.md)

---

### Week 3-4: 데이터 수집 및 관리

**학습 목표**
- 다양한 데이터 수집 방법 이해
- 데이터 거버넌스 및 동의 관리 개념 파악
- Query Service를 통한 데이터 분석 방법 학습

**주요 학습 내용**

1. **Data Ingestion**
   - Batch Ingestion vs Streaming Ingestion
   - Source Connectors (S3, Salesforce, Database 등)
   - Web SDK 구현
   - Mobile SDK 개요
   - API 직접 수집

2. **Data Governance**
   - DULE 레이블 (C1, C2, C3, I1, I2, I3)
   - Data Policies 설정
   - Consent Management (Opt-in, Opt-out)
   - 데이터 사용 제한 및 모니터링

3. **Query Service**
   - PostgreSQL 문법 기반 쿼리
   - 프로필 데이터 조회 및 분석
   - 이벤트 데이터 시계열 분석
   - 데이터 집계 및 변환

**실습 프로젝트**
- [ ] Web SDK 구현 (HTML 페이지)
- [ ] 배치 수집 워크플로우 구축
- [ ] 스트리밍 수집 테스트
- [ ] 데이터 레이블 적용
- [ ] 데이터 정책 생성
- [ ] Query Service로 프로필 분석

**학습 체크리스트**
- [ ] Batch와 Streaming 수집의 차이 이해
- [ ] Web SDK를 통한 데이터 수집 구현
- [ ] 배치 수집 워크플로우 구축
- [ ] DULE 레이블의 의미와 용도 이해
- [ ] 데이터 정책의 작동 원리 이해
- [ ] Query Service 기본 쿼리 작성 가능
- [ ] 프로필 데이터 분석 쿼리 작성 완료

**참고 문서**: [docs/week3-4-data-ingestion.md](docs/week3-4-data-ingestion.md)

---

### Week 5-6: 세그멘테이션 및 오디언스

**학습 목표**
- Segmentation Service의 작동 원리 이해
- 다양한 세그먼트 유형 생성 및 평가
- 오디언스 활용 방법 학습

**주요 학습 내용**

1. **Segmentation Service**
   - Segment Builder UI 활용
   - Profile-Attribute 세그먼트
   - Event-Based 세그먼트
   - Time-Based 세그먼트
   - PQL (Profile Query Language)

2. **오디언스 평가 방법**
   - Edge Segmentation (클라이언트 측 실시간)
   - Streaming Segmentation (서버 측 실시간)
   - Batch Segmentation (주기적 평가)
   - 세그먼트 작업 스케줄링

3. **세그먼트 분석**
   - 세그먼트 집계 및 크기 측정
   - 세그먼트 중복 분석
   - 증분 업데이트 모니터링

4. **Audience Composition** (선택)
   - 세그먼트 조합 (교집합, 합집합, 차집합)
   - 복잡한 오디언스 생성

**실습 프로젝트**
- [ ] 행동 기반 세그먼트 생성
- [ ] 인구통계 기반 세그먼트 생성
- [ ] 다중 엔티티 세그먼트 생성
- [ ] 스트리밍 세그먼트 성능 테스트
- [ ] 세그먼트 중복 분석

**5가지 비즈니스 시나리오 세그먼트**
1. **행동 기반**: 지난 7일 내 구매 전환한 고객
2. **행동 기반**: 장바구니를 버린 고객
3. **인구통계 기반**: Premium 멤버십 20대 여성 고객
4. **인구통계 기반**: 500포인트 이상 보유 고객
5. **다중 엔티티**: 특정 제품 카테고리 구매 + 특정 지역 거주 고객

**학습 체크리스트**
- [ ] Segment Builder UI로 세그먼트 생성 가능
- [ ] 행동 기반 세그먼트 생성 완료
- [ ] 인구통계 기반 세그먼트 생성 완료
- [ ] 다중 엔티티 세그먼트 생성 완료
- [ ] 스트리밍 vs 배치 차이 이해
- [ ] 세그먼트 중복 분석 완료
- [ ] 스트리밍 세그먼트 성능 테스트 완료

**참고 문서**: [docs/week5-6-segmentation.md](docs/week5-6-segmentation.md)

---

### Week 7-8: 활성화 및 통합

**학습 목표**
- Destinations의 작동 원리 이해
- 다양한 목적지로의 데이터 활성화 구현
- Journey Optimizer와 AI 서비스 개요 파악

**주요 학습 내용**

1. **Destinations**
   - 스트리밍 vs 배치 목적지
   - Profile Export vs Audience Export
   - 주요 목적지 유형:
     - 광고 플랫폼 (Google Ads, Facebook, LinkedIn)
     - 이메일/마케팅 플랫폼 (Salesforce, Mailchimp, Eloqua)
     - 데이터 웨어하우스 (S3, BigQuery, Azure Blob)
     - 커스텀 통합 (HTTP API, SFTP)

2. **활성화 워크플로우**
   - 목적지 연결 및 인증
   - 필드 매핑
   - 세그먼트 선택
   - 스케줄 설정
   - 데이터플로우 모니터링

3. **Journey Optimizer** (선택)
   - Journey Designer
   - AI 기반 Decisioning
   - 다채널 메시징 (이메일, SMS, 푸시)

4. **AI 서비스** (선택)
   - Customer AI (이탈 예측, 생애 가치)
   - Attribution AI (채널 기여도 분석)

**실습 프로젝트**
- [ ] Google Ads 활성화 설정
- [ ] 이메일 플랫폼 활성화 설정
- [ ] 커스텀 HTTP 엔드포인트 활성화
- [ ] 데이터플로우 모니터링
- [ ] API를 통한 세그먼트 내보내기

**학습 체크리스트**
- [ ] Destinations의 작동 원리 이해
- [ ] 스트리밍 vs 배치 목적지 차이 이해
- [ ] Profile Export vs Audience Export 차이 이해
- [ ] 3개 이상의 목적지 설정 완료
- [ ] 활성화 데이터플로우 모니터링 완료
- [ ] API를 통한 세그먼트 내보내기 완료
- [ ] Journey Optimizer 기능 파악 (선택)
- [ ] Customer AI 기능 파악 (선택)

**참고 문서**: [docs/week7-8-activation.md](docs/week7-8-activation.md)

---

## 최종 프로젝트: End-to-End 데이터 파이프라인

8주 학습을 마무리하며 전체 워크플로우를 통합하는 최종 프로젝트를 진행합니다.

**프로젝트 목표**
실제 e-커머스 시나리오를 기반으로 데이터 수집부터 활성화까지 전체 파이프라인 구축

**프로젝트 단계**

1. **스키마 설계**
   - Customer Profile 스키마
   - Web Page View Events 스키마
   - Commerce Events 스키마

2. **데이터 수집**
   - Web SDK 구현 (HTML 페이지)
   - Pageview, Add-to-Cart, Purchase 이벤트 수집
   - 배치 데이터 업로드 (과거 고객 데이터)

3. **Identity 설정**
   - Email Namespace
   - Phone Namespace
   - Identity Graph 구축

4. **세그먼트 생성** (최소 5개)
   - Cart Abandoners (장바구니 이탈)
   - VIP Customers (고가치 고객)
   - New Customers (신규 고객)
   - Inactive Customers (비활성 고객)
   - Repeat Buyers (재구매 고객)

5. **활성화**
   - Google Ads 연동
   - 이메일 플랫폼 연동
   - 커스텀 HTTP 엔드포인트 연동

6. **모니터링 및 분석**
   - 데이터 수집 모니터링
   - 세그먼트 크기 트래킹
   - 활성화 성공률 측정

**참고 문서**: [projects/final-project/README.md](projects/final-project/README.md)

---

## 학습 리소스

### Adobe 공식 문서
- [Experience League Documentation](https://experienceleague.adobe.com/docs/experience-platform.html)
- [API Reference](https://www.adobe.io/apis/experienceplatform/home/api-reference.html)
- [Postman Collection](https://www.postman.com/adobe-experience-platform-ecosystem/)

### 개발 도구
- [Adobe Experience Platform Debugger](https://chrome.google.com/webstore/detail/adobe-experience-cloud-de/ocdmogmohccmeicdhlhhgeaonijenmgj)
- [Web SDK GitHub](https://github.com/adobe/alloy)

### 환경 설정
- [설정 가이드](setup/)
- [Postman 환경 템플릿](setup/postman-env-template.json)

---

## 학습 팁

1. **순차적 학습**: 주차별로 순서대로 학습하세요. 이전 주차의 개념이 다음 주차의 기반이 됩니다.

2. **실습 우선**: 이론 학습 후 반드시 실습 프로젝트를 완료하세요. 실무 경험이 가장 중요합니다.

3. **체크리스트 활용**: 각 주차별 학습 체크리스트를 활용하여 학습 완료도를 확인하세요.

4. **샌드박스 활용**: 실습 시 반드시 개발 샌드박스를 사용하고, 프로덕션 환경은 피하세요.

5. **커뮤니티 참여**: Adobe Experience League 커뮤니티에서 다른 학습자들과 소통하세요.

6. **API 테스트**: Postman을 활용하여 API 호출을 직접 테스트해보세요.

7. **문서 참조**: Adobe 공식 문서를 자주 참조하여 최신 기능과 베스트 프랙티스를 확인하세요.

---

## 학습 완료 후 다음 단계

- Adobe Experience Platform 인증 준비
- 실무 프로젝트 적용
- Journey Optimizer, Customer AI 등 고급 기능 학습
- Real-Time CDP 활용 심화 학습
- Adobe Analytics와의 통합 학습

---

## 문의 및 지원

- 각 주차별 상세 내용은 [docs/](docs/) 폴더 참조
- 실습 가이드는 [projects/](projects/) 폴더 참조
- 샘플 데이터는 [samples/data/](samples/data/) 폴더 참조
- Adobe Experience League 커뮤니티 활용
