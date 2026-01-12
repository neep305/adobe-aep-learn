# Week 3-4: 데이터 수집 및 관리

## 학습 목표
- 다양한 데이터 수집 방법 이해
- 데이터 거버넌스 및 동의 관리 개념 파악
- Query Service를 통한 데이터 분석 방법 학습

## 1. Data Ingestion

### Batch vs Streaming

#### Batch Ingestion
- **용도**: 대량의 과거 데이터 또는 정기적인 업데이트
- **장점**: 비용 효율적, 대용량 처리 가능
- **제한사항**: 실시간성 부족
- **용량**: 최대 512MB 단일 파일

#### Streaming Ingestion
- **용도**: 실시간 데이터 수집
- **장점**: 즉시 처리, 낮은 지연시간
- **제한사항**: 상대적으로 높은 비용
- **처리량**: 초당 수천 개의 이벤트

### 수집 방법

#### 1. Source Connectors
- Amazon S3, Google Cloud Storage 등 클라우드 스토리지
- Salesforce, ServiceNow 등 CRM/SaaS 시스템
- Database 커넥터 (Oracle, MySQL 등)

#### 2. Web SDK
Adobe의 표준 웹 데이터 수집 라이브러리
```javascript
// 기본 설정
alloy("configure", {
  "edgeConfigId": "YOUR_CONFIG_ID",
  "orgId": "YOUR_ORG_ID"
});

// 이벤트 전송
alloy("sendEvent", {
  "xdm": {
    "eventType": "web.webpagedetails.pageViews",
    "web": {
      "webPageDetails": {
        "URL": "https://example.com"
      }
    }
  }
});
```

#### 3. Mobile SDK
- iOS/Android 네이티브 앱용 SDK
- React Native, Flutter 등 크로스 플랫폼 지원

#### 4. API 직접 수집
- RESTful API를 통한 직접 데이터 전송
- 백엔드 시스템에서 직접 호출 시 사용

### 실습 가이드
1. [Web SDK 구현](./projects/week3-4/implement-web-sdk.md)
2. [배치 수집](./projects/week3-4/batch-ingestion.md)
3. [스트리밍 수집](./projects/week3-4/streaming-ingestion.md)

## 2. Data Governance

### DULE (Data Usage Labeling & Enforcement)

#### Data Labels
데이터에 메타데이터를 추가하여 사용 범위를 제한합니다:
- **C1**: 계약 데이터 (이름, 주소, 이메일 등)
- **C2**: 개인 식별 정보 (PII)
- **C3**: 민감한 데이터 (신용카드, SSN 등)
- **I1**: 특정 목적을 위한 데이터
- **I2**: 분석 목적 데이터
- **I3**: 마케팅 데이터

#### Data Policies
레이블 기반으로 데이터 사용 규칙을 적용합니다:
- 특정 목적지로의 전송 제한
- 특정 용도로의 사용 제한
- 마케팅 채널별 데이터 사용 제한

### Consent Management
사용자의 동의 정보를 관리합니다:
- **Opt-in**: 사용자가 명시적으로 동의
- **Opt-out**: 사용자가 동의 철회
- **No Preference**: 사용자가 선호사항을 표현하지 않음

### 실습 가이드
1. [데이터 레이블 적용](./projects/week3-4/apply-data-labels.md)
2. [데이터 정책 생성](./projects/week3-4/create-data-policy.md)
3. [동의 정보 수집](./projects/week3-4/consent-management.md)

## 3. Query Service

### 개념
Adobe Experience Platform의 데이터 분석을 위한 SQL 쿼리 서비스입니다.

### 주요 기능
- PSQL (PostgreSQL) 문법 지원
- 데이터셋 쿼리 및 분석
- 세그먼트 정의 및 고급 세그먼테이션
- 데이터 변환 및 집계

### 기본 쿼리 패턴

#### 프로필 데이터 조회
```sql
SELECT * FROM profile_table LIMIT 10;
```

#### 이벤트 데이터 조회
```sql
SELECT * FROM event_table 
WHERE timestamp >= '2023-01-01' 
LIMIT 100;
```

#### 데이터 집계
```sql
SELECT city, COUNT(*) as customer_count
FROM profile_table
GROUP BY city
ORDER BY customer_count DESC;
```

### 고급 기능
- 시간대별 분석 (Temporal Joins)
- 세그먼트 대비 (Segment Comparisons)
- 데이터 변환 및 파생 필드 생성

### 실습 가이드
1. [기본 쿼리 작성](./projects/week3-4/basic-queries.md)
2. [복잡한 분석 쿼리](./projects/week3-4/advanced-queries.md)
3. [프로필 데이터 분석](./projects/week3-4/profile-analysis.md)

## 학습 체크리스트

- [ ] Batch와 Streaming 수집의 차이 이해
- [ ] Web SDK를 통한 데이터 수집 구현
- [ ] 배치 수집 워크플로우 구축
- [ ] DULE 레이블의 의미와 용도 이해
- [ ] 데이터 정책의 작동 원리 이해
- [ ] Query Service 기본 쿼리 작성 가능
- [ ] 프로필 데이터 분석 쿼리 작성 완료

## 참고 자료
- [데이터 수집 개요](https://experienceleague.adobe.com/docs/experience-platform/ingestion/home.html)
- [Web SDK 문서](https://experienceleague.adobe.com/docs/experience-platform/edge/home.html)
- [Data Governance](https://experienceleague.adobe.com/docs/experience-platform/data-governance/home.html)
- [Query Service 가이드](https://experienceleague.adobe.com/docs/experience-platform/query/home.html)

