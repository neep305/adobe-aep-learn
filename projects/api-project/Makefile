# Makefile for AEP API Project
# Windows에서는 'make' 대신 직접 명령어 사용 권장

.PHONY: help build up down restart logs test clean

help: ## 도움말 표시
	@echo "사용 가능한 명령어:"
	@echo "  make build    - Docker 이미지 빌드"
	@echo "  make up       - 개발 모드로 서버 시작"
	@echo "  make down     - 서버 중지"
	@echo "  make restart  - 서버 재시작"
	@echo "  make logs     - 로그 확인"
	@echo "  make test     - 테스트 실행"
	@echo "  make clean    - Docker 리소스 정리"

build: ## Docker 이미지 빌드
	docker-compose build

up: ## 개발 모드로 서버 시작
	docker-compose up

up-d: ## 백그라운드로 서버 시작
	docker-compose up -d

down: ## 서버 중지
	docker-compose down

restart: ## 서버 재시작
	docker-compose restart

logs: ## 로그 확인
	docker-compose logs -f

ps: ## 컨테이너 상태 확인
	docker-compose ps

test: ## 테스트 실행
	docker-compose exec aep-api pytest

test-local: ## 로컬 환경에서 테스트
	pytest

shell: ## 컨테이너 접속
	docker-compose exec aep-api bash

clean: ## Docker 리소스 정리
	docker-compose down -v --rmi all

prod-up: ## 프로덕션 모드로 서버 시작
	docker-compose -f docker-compose.prod.yaml up -d

prod-down: ## 프로덕션 서버 중지
	docker-compose -f docker-compose.prod.yaml down

format: ## 코드 포맷팅
	black .
	isort .

lint: ## 린팅
	flake8 .
	mypy .
