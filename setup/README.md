# AEP 학습 환경 설정 가이드

## 1. AEP 계정 설정

### Trial 계정 생성
1. [Adobe Experience Cloud](https://experience.adobe.com) 접속
2. Trial 계정 신청
3. 샌드박스 생성 (Development 샌드박스 권장)

### 필요한 권한
- Schema Management 권한
- Dataset Management 권한
- Profile Management 권한
- Segment Management 권한
- Destination Management 권한

## 2. API 접근 설정

### 인증 정보 수집
```
Organization ID: [확인 필요]
API Key: [확인 필요]
Client Secret: [확인 필요]
Sandbox Name: [확인 필요]
Access Token: [확인 필요]
```

### API 사용자 생성
1. Adobe Admin Console 접속
2. Products → Adobe Experience Platform → API Users
3. 사용자 생성 및 권한 할당

## 3. Postman 설정

### Collection 가져오기
1. Postman 설치
2. Adobe에서 공식 AEP Postman Collection 다운로드
3. Collection Import

### Environment 변수 설정
```
organizationId: [값]
apiKey: [값]
clientSecret: [값]
accessToken: [값]
sandboxName: [값]
```

## 4. 샘플 데이터 준비

### Luma Demo 데이터
- [Experience League Demo 환경](https://experienceleague.adobe.com/docs/platform-learn/tutorials/intro-to-platform/using-postman-api.html) 참조

### CSV 샘플 데이터
- `samples/data/` 디렉토리에 샘플 파일 제공

## 5. 개발 도구 설치

### Query Service 접근 도구
```bash
# PostgreSQL 클라이언트 설치
brew install postgresql  # macOS
# 또는 pgAdmin 설치
```

### Web SDK 실습 환경
```bash
# Node.js 설치 (v14 이상)
brew install node

# 간단한 웹 서버 사용
npx http-server
```

## 다음 단계

환경 설정이 완료되면 Week 1-2 학습으로 진행하세요.

