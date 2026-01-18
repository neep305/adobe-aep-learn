"""
Adobe Experience Platform OAuth 2.0 인증 헬퍼
Access Token 자동 발급 및 갱신

Adobe IMS는 더 이상 JWT 인증을 지원하지 않습니다.
OAuth 2.0 Server-to-Server (Client Credentials) 또는
OAuth 2.0 Device Authorization Flow를 사용하세요.

사용법:
    python auth_helper.py --generate-token
    python auth_helper.py --validate-token
"""

import os
import sys
import json
import time
import requests
import argparse
from pathlib import Path
from typing import Optional, Dict, Tuple
from dotenv import load_dotenv, set_key
from datetime import datetime, timedelta

# 환경 변수 로드
load_dotenv()


class AEPAuthHelper:
    """Adobe Experience Platform OAuth 2.0 인증 헬퍼"""

    def __init__(self):
        """인증 정보 초기화"""
        self.api_key = os.getenv('API_KEY')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.ims_org = os.getenv('IMS_ORG')
        self.ims_endpoint = os.getenv('IMS_ENDPOINT', 'https://ims-na1.adobelogin.com')

        # OAuth 2.0 Scopes (Server-to-Server 인증용)
        # AEP API 접근에 필요한 scopes
        self.oauth_scopes = os.getenv(
            'OAUTH_SCOPES',
            'openid,AdobeID,read_organizations,additional_info.projectedProductContext,session'
        )

    def generate_client_credentials_token(self) -> Tuple[bool, Optional[Dict]]:
        """
        OAuth 2.0 Client Credentials Flow (Server-to-Server 인증)

        Adobe Developer Console에서 OAuth Server-to-Server 자격 증명으로
        생성된 프로젝트에서 사용합니다.
        """
        print("\n--- OAuth 2.0 Client Credentials Flow ---")

        url = f"{self.ims_endpoint}/ims/token/v3"

        data = {
            'client_id': self.api_key,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': self.oauth_scopes
        }

        try:
            response = requests.post(url, data=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                access_token = result.get('access_token')
                expires_in = result.get('expires_in', 86400)  # 기본 24시간

                print(f"[OK] Access Token 발급 완료")
                print(f"  - Token: {access_token[:50]}...")
                print(f"  - 유효기간: {expires_in // 3600}시간")

                return True, result
            else:
                error = response.json() if response.text else {}
                print(f"[ERROR] Access Token 발급 실패: HTTP {response.status_code}")
                print(f"   {json.dumps(error, indent=2, ensure_ascii=False)}")
                return False, error

        except Exception as e:
            print(f"[ERROR] 요청 실패: {e}")
            return False, None

    def oauth_device_flow(self) -> Tuple[bool, Optional[Dict]]:
        """
        OAuth 2.0 Device Authorization Flow (사용자 인증)

        브라우저에서 사용자가 직접 로그인하는 방식입니다.
        개발/테스트 환경에서 사용하거나 Server-to-Server 자격 증명이
        없는 경우 사용합니다.
        """
        print("\n--- OAuth 2.0 Device Authorization Flow ---")
        print("참고: 이 방법은 사용자 인증용입니다.")
        print("      프로덕션에서는 OAuth Server-to-Server를 사용하세요.")

        # Step 1: Device Code 요청
        device_auth_url = f"{self.ims_endpoint}/ims/authorize/v2/device"

        data = {
            'client_id': self.api_key,
            'scope': self.oauth_scopes
        }

        try:
            response = requests.post(device_auth_url, data=data, timeout=30)

            if response.status_code != 200:
                print(f"[ERROR] Device Code 요청 실패: HTTP {response.status_code}")
                return False, None

            device_info = response.json()
            verification_url = device_info.get('verification_url')
            user_code = device_info.get('user_code')
            device_code = device_info.get('device_code')
            interval = device_info.get('interval', 5)

            print(f"\n브라우저에서 다음 URL을 여세요:")
            print(f"  {verification_url}")
            print(f"\n코드를 입력하세요:")
            print(f"  {user_code}")
            print(f"\n인증 대기 중...")

            # Step 2: Polling으로 Access Token 대기
            token_url = f"{self.ims_endpoint}/ims/token/v3"
            max_attempts = 60  # 5분 대기

            for attempt in range(max_attempts):
                time.sleep(interval)

                token_data = {
                    'client_id': self.api_key,
                    'device_code': device_code,
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
                }

                token_response = requests.post(token_url, data=token_data, timeout=30)

                if token_response.status_code == 200:
                    result = token_response.json()
                    access_token = result.get('access_token')

                    print(f"\n[OK] Access Token 발급 완료!")
                    print(f"  - Token: {access_token[:50]}...")

                    return True, result

                elif token_response.status_code == 400:
                    error = token_response.json()
                    error_code = error.get('error')

                    if error_code == 'authorization_pending':
                        # 아직 인증 대기 중
                        print(f"  대기 중... ({attempt + 1}/{max_attempts})")
                        continue
                    elif error_code == 'slow_down':
                        # Polling 속도 줄이기
                        interval += 5
                        continue
                    elif error_code == 'expired_token':
                        print(f"\n[ERROR] 시간 초과: Device Code가 만료되었습니다.")
                        return False, None
                    else:
                        print(f"\n[ERROR] 인증 실패: {error_code}")
                        return False, error

            print(f"\n[ERROR] 타임아웃: 최대 대기 시간을 초과했습니다.")
            return False, None

        except Exception as e:
            print(f"[ERROR] OAuth Device Flow 실패: {e}")
            return False, None

    def validate_access_token(self, access_token: Optional[str] = None) -> bool:
        """Access Token 유효성 검증"""
        if not access_token:
            access_token = os.getenv('ACCESS_TOKEN')

        if not access_token:
            print("[ERROR] Access Token이 없습니다.")
            return False

        print("\n--- Access Token 유효성 검증 ---")

        # Platform API에 테스트 요청
        test_url = f"{os.getenv('PLATFORM_GATEWAY', 'https://platform.adobe.io')}/data/foundation/schemaregistry/tenant/schemas"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-api-key': self.api_key,
            'x-gw-ims-org-id': self.ims_org,
            'x-sandbox-name': os.getenv('SANDBOX_NAME', 'prod'),
            'Accept': 'application/vnd.adobe.xed-full+json; version=1'
        }

        try:
            response = requests.get(test_url, headers=headers, timeout=30)

            if response.status_code == 200:
                print(f"[OK] Access Token이 유효합니다.")
                return True
            elif response.status_code == 401:
                print(f"[ERROR] Access Token이 만료되었거나 유효하지 않습니다.")
                return False
            else:
                print(f"[WARNING] 검증 실패: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 검증 요청 실패: {e}")
            return False

    def update_env_file(self, access_token: str, token_info: Optional[Dict] = None):
        """새로운 Access Token을 .env 파일에 업데이트"""
        env_path = Path(__file__).parent / '.env'

        if not env_path.exists():
            print(f"[ERROR] .env 파일을 찾을 수 없습니다: {env_path}")
            return

        try:
            set_key(str(env_path), 'ACCESS_TOKEN', access_token)
            print(f"\n[OK] .env 파일 업데이트 완료")
            print(f"  새로운 ACCESS_TOKEN이 저장되었습니다.")

            if token_info:
                expires_in = token_info.get('expires_in', 86400)
                expiry_time = datetime.now() + timedelta(seconds=expires_in)
                print(f"  만료 시간: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            print(f"[ERROR] .env 파일 업데이트 실패: {e}")

    def generate_and_update_token(self, method: str = 'client_credentials'):
        """토큰 생성 및 .env 파일 업데이트 (전체 프로세스)"""
        print(f"\n{'='*60}")
        print(f"Access Token 생성 시작 (방법: {method.upper()})")
        print(f"{'='*60}")

        if method == 'client_credentials':
            # OAuth 2.0 Client Credentials (Server-to-Server)
            success, result = self.generate_client_credentials_token()
            if not success:
                return False

            access_token = result.get('access_token')
            self.update_env_file(access_token, result)

            # 검증
            if self.validate_access_token(access_token):
                print(f"\n[OK] 토큰 생성 및 검증 완료!")
                return True
            else:
                print(f"\n[ERROR] 토큰 검증 실패")
                return False

        elif method == 'device':
            # OAuth 2.0 Device Authorization Flow
            success, result = self.oauth_device_flow()
            if not success:
                return False

            access_token = result.get('access_token')
            self.update_env_file(access_token, result)

            print(f"\n[OK] 토큰 생성 완료!")
            return True

        else:
            print(f"[ERROR] 지원하지 않는 인증 방법: {method}")
            print(f"   사용 가능: client_credentials, device")
            return False


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='Adobe Experience Platform OAuth 2.0 인증 헬퍼',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # OAuth Client Credentials로 Access Token 생성 (권장)
  python auth_helper.py --generate-token

  # OAuth Device Flow로 토큰 생성 (사용자 인증)
  python auth_helper.py --generate-token --method device

  # 현재 Access Token 검증
  python auth_helper.py --validate-token

참고:
  - OAuth Server-to-Server는 Adobe Developer Console에서 설정이 필요합니다
  - Device Flow는 브라우저에서 사용자 로그인이 필요합니다
  - Access Token은 24시간 후 만료됩니다
  - JWT 인증은 더 이상 지원되지 않습니다 (2024년 1월 서비스 종료)
        """
    )

    parser.add_argument('--generate-token', action='store_true',
                       help='새로운 Access Token 생성 및 .env 파일 업데이트')
    parser.add_argument('--validate-token', action='store_true',
                       help='현재 Access Token 유효성 검증')
    parser.add_argument('--method', type=str, choices=['client_credentials', 'device'],
                       default='client_credentials',
                       help='인증 방법 선택 (기본값: client_credentials)')

    args = parser.parse_args()

    # 명령어가 없으면 도움말 출력
    if not (args.generate_token or args.validate_token):
        parser.print_help()
        return

    # Auth Helper 초기화
    auth = AEPAuthHelper()

    # 명령 실행
    if args.validate_token:
        is_valid = auth.validate_access_token()
        sys.exit(0 if is_valid else 1)

    elif args.generate_token:
        success = auth.generate_and_update_token(method=args.method)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
