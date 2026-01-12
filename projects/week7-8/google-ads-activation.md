# 실습: Google Ads 활성화

## 목표
AEP 세그먼트를 Google Ads 캠페인에 활성화합니다.

## 사전 준비
- Google Ads 계정 (관리자 권한)
- Google Ads Customer ID 확인
- AEP 계정에서 Destination 활성화 권한

## 1. Google Ads 연결 설정

### AEP UI에서 설정
1. Platform UI → Destinations 메뉴 접근
2. **Browse** 탭에서 "Google Ads" 검색
3. **Set up** 클릭

### 계정 연결
1. **New account** 선택
2. Account 정보 입력:
   - Name: "Google Ads Production"
   - Description: "Google Ads campaign activation"
3. **Connect to destination** 클릭

### Google Ads 로그인
1. Google 계정으로 로그인
2. Google Ads 계정 선택
3. 권한 승인

## 2. 데이터 흐름 구성

### Destination 설정
1. 연결된 Google Ads 계정 선택
2. **Next** 클릭

### 데이터 선택
1. 세그먼트 선택 (예: "Recent Visitors No Purchase")
2. 매핑 확인:
   - Email: 이메일 주소
   - Phone: 전화번호 (선택)
3. **Next** 클릭

### 스케줄 설정
1. 활성화 방법 선택:
   - **On segment evaluation**: 세그먼트 평가 시 자동 활성화
   - **Manual**: 수동 활성화
2. 활성화 일정 확인
3. **Next** 클릭

### 검토 및 완료
1. 설정 요약 확인
2. **Finish** 클릭

## 3. 활성화 모니터링

### 데이터 흐름 확인
1. Destinations → Browse에서 Google Ads 목적지 선택
2. **Dataflows** 탭 확인
3. 다음 정보 확인:
   - 상태 (Active/Inactive)
   - 마지막 활성화 시간
   - 활성화된 프로필 수

### 활성화 로그 확인
1. Platform UI → Monitoring 메뉴
2. **Streaming Activation** 탭
3. 활성화 이벤트 로그 확인

## 4. Google Ads에서 확인

### Audience Manager 확인
1. Google Ads 계정 로그인
2. **Tools & Settings** → **Audience Manager**
3. Shared Library → Customer Match 선택
4. 세그먼트 확인

### 캠페인에 적용
1. 캠페인 선택 또는 새 캠페인 생성
2. **Targeting** → **Audiences** 선택
3. Customer Match 오디언스 추가
4. Targeting 설정:
   - **Targeting**: 오디언스 타겟팅
   - **Observation**: 모니터링

## 검증

구성된 활성화가 다음 조건을 만족하는지 확인:
- [ ] Google Ads 연결이 정상적으로 설정됨
- [ ] 데이터 흐름이 Active 상태
- [ ] 세그먼트가 Google Ads에 업로드됨
- [ ] Audience Manager에서 오디언스 확인 가능
- [ ] 활성화 로그에 성공 이벤트가 기록됨

## 주의사항

### 데이터 요구사항
- 최소 1,000개의 유효한 이메일 주소
- 해시 처리된 데이터 사용 권장
- 최근 90일 내 활성 데이터

### 개인정보 보호
- Google의 Customer Match 정책 준수 필수
- 사용자 동의 정보 확인
- DULE 레이블 및 데이터 정책 준수

## 다음 단계
- [이메일 플랫폼 활성화](./email-activation.md)

