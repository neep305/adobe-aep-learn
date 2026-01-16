# Adobe Experience Platform API Documentation Server

FastAPI 기반 AEP API 엔드포인트 문서화 및 테스트 서버입니다.

## 📋 프로젝트 구조

```
api-project/
├── main.py                 # FastAPI 앱 진입점
├── config.py              # AEP 인증 설정
├── requirements.txt       # Python 패키지 의존성
├── .env.example          # 환경 변수 템플릿
├── models/               # Pydantic 데이터 모델
│   ├── schema.py         # XDM Schema 모델
│   ├── identity.py       # Identity 모델
│   └── profile.py        # Profile 모델
├── routers/              # API 라우터
│   ├── schema_registry.py # Schema Registry API
│   ├── identity.py       # Identity Service API
│   ├── profile.py        # Profile API
│   ├── segmentation.py   # Segmentation API
│   └── destinations.py   # Destinations API
└── services/             # 비즈니스 로직
    └── adobe_client.py   # Adobe API 클라이언트
```

## 🚀 빠른 시작

### 방법 1: Docker로 실행 (권장) 🐳

#### 1. 환경 변수 설정

```powershell
# 기존 _env 파일이 있다면 내용 확인
cat _env

# _env 파일의 내용을 참조하여 .env 파일 생성/수정
# 또는 .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 열어 Adobe 인증 정보 입력
notepad .env
```

> **참고**: 프로젝트에 `_env` 파일이 이미 있다면 해당 내용을 `.env` 파일로 옮기거나 참조하세요.

#### 2. Docker Compose로 실행

```powershell
# 개발 모드 (코드 변경 시 자동 재시작)
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f aep-api

# 중지
docker-compose down
```

#### 3. 프로덕션 모드 실행

```powershell
# 프로덕션용 docker-compose 사용
docker-compose -f docker-compose.prod.yaml up --build -d
```

#### 4. API 문서 확인

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

### 방법 2: 로컬 Python 환경 실행

#### 1. 가상환경 설정

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# 패키지 설치
pip install -r requirements.txt
```

#### 2. 환경 변수 설정

```powershell
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 열어 Adobe 인증 정보 입력
notepad .env
```

#### 3. 서버 실행

```powershell
# 개발 모드 (자동 재시작)
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 주요 API 엔드포인트

### Schema Registry API
- `GET /api/schema-registry/schemas` - 스키마 목록 조회
- `GET /api/schema-registry/schemas/{schemaId}` - 특정 스키마 조회
- `GET /api/schema-registry/classes` - 클래스 목록 조회
- `GET /api/schema-registry/fieldgroups` - 필드 그룹 목록 조회

### Identity Service API
- `GET /api/identity/namespaces` - Identity Namespace 목록
- `POST /api/identity/identity-graph` - Identity Graph 조회

### Real-Time Customer Profile API
- `GET /api/profile/entities` - 프로필 조회
- `GET /api/profile/merge-policies` - Merge Policy 목록

### Segmentation API
- `GET /api/segmentation/segment-definitions` - 세그먼트 정의 목록
- `GET /api/segmentation/segment-jobs` - 세그먼트 작업 목록

### Destinations API
- `GET /api/destinations/destinations` - 대상 목록 조회
- `GET /api/destinations/dataflows` - 데이터 플로우 목록

## 🔐 Adobe 인증 설정

### Access Token 발급 방법

1. **Adobe Developer Console** 접속
   - https://developer.adobe.com/console

2. **프로젝트 생성 또는 선택**

3. **API 추가**
   - Experience Platform API 선택

4. **인증 정보 확인**
   - Client ID (API Key)
   - Client Secret
   - Technical Account ID
   - Organization ID

5. **Access Token 생성**
   - Postman 또는 curl로 JWT 토큰 교환
   - 발급된 Access Token을 `.env` 파일에 입력

## 🐳 Docker 명령어

### 컨테이너 관리

```powershell
# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 재시작
docker-compose restart
🏗️ 아키텍처

```
┌─────────────────┐
│   Client        │
│  (Browser/API)  │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  FastAPI Server │
│  (Port 8000)    │
│                 │
│  ├─ Routers     │
│  ├─ Models      │
│  └─ Services    │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Adobe AEP API  │
│  platform.adobe │
│  .io            │
└─────────────────┘
```

## 📖 참고 자료

- [Adobe Experience Platform API Reference](https://developer.adobe.com/experience-platform-apis/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose
docker-compose exec aep-api bash

# 빌드 캐시 없이 재빌드
docker-compose build --no-cache
docker-compose up -d
```

### 로그 및 모니터링

```powershell
# 실시간 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f aep-api

# 최근 100줄 로그
docker-compose logs --tail=100 aep-api
```

### 정리

```powershell
# 컨테이너 중지 및 삭제
docker-compose down

# 볼륨까지 삭제
docker-compose down -v

# 이미지까지 삭제
docker-compose down --rmi all
```

## 🧪 테스트

```powershell
# 로컬 환경에서 테스트
pytest

# 커버리지 포함
pytest --cov=.

# Docker 환경에서 테스트
docker-compose exec aep-api pytest
```

## 📖 참고 자료

- [Adobe Experience Platform API Reference](https://developer.adobe.com/experience-platform-apis/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🛠️ 개발 가이드

### 새로운 API 엔드포인트 추가

1. `models/` 디렉토리에 Pydantic 모델 정의
2. `routers/` 디렉토리에 라우터 생성
3. `main.py`에 라우터 등록
4. `services/adobe_client.py`에 API 호출 로직 추가

### 코드 포맷팅

```powershell
# Black으로 코드 포맷팅
black .

# Flake8으로 린팅
flake8 .
```
