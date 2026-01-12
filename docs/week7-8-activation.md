# Week 7-8: 활성화 및 통합

## 학습 목표
- Destinations의 작동 원리 이해
- 다양한 목적지로의 데이터 활성화 구현
- Journey Optimizer와 AI 서비스 개요 파악

## 1. Destinations

### 개념
Adobe Experience Platform에서 수집한 데이터를 다양한 외부 시스템으로 전송하는 기능입니다.

### 스트리밍 vs 배치 목적지

#### 스트리밍 Destinations
- **장점**: 실시간 데이터 전송, 낮은 지연시간
- **사용 사례**: 실시간 광고 타겟팅, 개인화 엔진
- **대표적인 목적지**: Facebook, Google Ads

#### 배치 Destinations
- **장점**: 대용량 데이터 전송, 비용 효율적
- **사용 사례**: 이메일 마케팅, 정기적인 데이터 동기화
- **대표적인 목적지**: SFTP, Amazon S3, Marketo

### Profile Export vs Audience Export

#### Profile Export
개별 프로필의 모든 속성을 전송
- **사용 시**: 프로필 정보가 필요한 시스템으로 전송
- **예시**: CRM 시스템, 이메일 플랫폼

#### Audience Export
세그먼트 멤버십 정보만 전송
- **사용 시**: 광고 플랫폼, 간단한 타겟팅
- **예시**: Facebook Custom Audiences, Google Customer Match

### 주요 목적지 유형

#### 광고 플랫폼
- **Google Ads**: Google 광고 캠페인 타겟팅
- **Facebook**: Facebook/Instagram 광고 타겟팅
- **LinkedIn**: LinkedIn 광고 타겟팅

#### 이메일/마케팅 플랫폼
- **Salesforce Marketing Cloud**: 이메일 마케팅
- **Mailchimp**: 이메일 캠페인
- **Oracle Eloqua**: 마케팅 자동화

#### 데이터 웨어하우스
- **Amazon S3**: 클라우드 스토리지
- **Google BigQuery**: 데이터 분석
- **Azure Blob Storage**: 클라우드 스토리지

#### 커스텀 통합
- **HTTP API**: 웹훅, REST API
- **SFTP**: 파일 기반 데이터 전송

### 실습 가이드
1. [Google Ads 활성화](./projects/week7-8/google-ads-activation.md)
2. [이메일 플랫폼 활성화](./projects/week7-8/email-activation.md)
3. [커스텀 HTTP 활성화](./projects/week7-8/custom-http-activation.md)

## 2. Journey Optimizer (선택)

### 개념
고객 여정을 실시간으로 관리하고 최적화하는 플랫폼입니다.

### 주요 기능
- **Journey Designer**: 시각적 여정 설계
- **Decisioning**: AI 기반 의사결정 엔진
- **Messaging**: 이메일, SMS, 푸시 알림

### 사용 사례
- 웰컴 여정
- 장바구니 이탈 복구
- 생일 프로모션

## 3. Customer AI / Attribution AI (선택)

### Customer AI
- **용도**: 고객 이탈 가능성 예측, 생애 가치 예측
- **입력**: 프로필 및 이벤트 데이터
- **출력**: 점수 및 인사이트

### Attribution AI
- **용도**: 마케팅 채널 효과 측정
- **입력**: 터치포인트 데이터
- **출력**: 채널별 기여도

## 학습 체크리스트

- [ ] Destinations의 작동 원리 이해
- [ ] 스트리밍 vs 배치 목적지 차이 이해
- [ ] Profile Export vs Audience Export 차이 이해
- [ ] 3개 이상의 목적지 설정 완료
- [ ] 활성화 데이터플로우 모니터링 완료
- [ ] API를 통한 세그먼트 내보내기 완료
- [ ] Journey Optimizer 기능 파악 (선택)
- [ ] Customer AI 기능 파악 (선택)

## 참고 자료
- [Destinations 개요](https://experienceleague.adobe.com/docs/experience-platform/destinations/home.html)
- [Journey Optimizer 문서](https://experienceleague.adobe.com/docs/journey-optimizer/using/ajo-home.html)
- [Customer AI 가이드](https://experienceleague.adobe.com/docs/experience-platform/intelligent-services/customer-ai/overview.html)

