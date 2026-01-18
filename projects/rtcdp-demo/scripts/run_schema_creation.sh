#!/bin/bash
# Adobe Experience Platform Schema 생성 스크립트 (macOS/Linux)
# 사용법: ./run_schema_creation.sh

set -e  # 에러 발생 시 즉시 중단

echo "============================================"
echo "AEP Schema Builder - 스키마 일괄 생성"
echo "============================================"
echo ""

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3가 설치되어 있지 않습니다."
    echo "Python 3.7 이상을 설치하세요: https://www.python.org/downloads/"
    exit 1
fi

echo "[1/4] Python 패키지 설치 중..."
pip3 install -q -r requirements.txt

echo "[2/4] 환경 설정 확인 중..."
if [ ! -f .env ]; then
    echo "[ERROR] .env 파일이 없습니다."
    echo "../.env.example을 복사하여 .env 파일을 생성하고 인증 정보를 입력하세요."
    exit 1
fi

echo "[3/4] Access Token 유효성 검증 중..."
if ! python3 auth_helper.py --validate-token; then
    echo ""
    echo "[WARNING] Access Token이 유효하지 않습니다."
    read -p "새로운 토큰을 생성하시겠습니까? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 auth_helper.py --generate-token
    else
        echo "토큰 생성을 건너뜁니다. .env 파일에서 ACCESS_TOKEN을 수동으로 업데이트하세요."
        exit 1
    fi
fi

echo ""
echo "[4/4] 스키마 생성 시작..."
echo ""

python3 aep_schema_builder.py --create-all

echo ""
echo "============================================"
echo "모든 스키마 생성이 완료되었습니다!"
echo "============================================"
echo ""
echo "다음 단계:"
echo "1. AEP UI에서 스키마 확인"
echo "2. Identity 네임스페이스 설정"
echo "3. Primary Identity 필드 지정"
echo "4. 데이터 수집 시작"
echo ""
