"""
Adobe Experience Platform API 설정
환경 변수를 통한 인증 정보 관리
"""
from pydantic_settings import BaseSettings
from typing import Optional


class AEPSettings(BaseSettings):
    """AEP API 인증 설정"""
    
    # Adobe IMS 인증
    api_key: str = ""
    client_secret: str = ""
    access_token: Optional[str] = None
    scopes: Optional[str] = None
    technical_account_id: str = ""
    ims: str = "https://ims-na1.adobelogin.com"
    ims_org: str = ""
    
    # Adobe Experience Platform 설정
    sandbox_name: str = "prod"
    tenant_id: str = ""
    container_id: str = "global"
    client_id: Optional[str] = None
    global_company_id: Optional[str] = None
    
    # API 엔드포인트
    platform_gateway: str = "https://platform.adobe.io"
    ims_endpoint: str = "https://ims-na1.adobelogin.com"
    
    # JWT 인증용 (선택사항)
    private_key_path: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = AEPSettings()


def get_aep_headers() -> dict:
    """AEP API 호출용 공통 헤더 생성"""
    return {
        "Authorization": f"Bearer {settings.access_token}",
        "x-api-key": settings.api_key,
        "x-gw-ims-org-id": settings.ims_org,
        "x-sandbox-name": settings.sandbox_name,
        "Content-Type": "application/json",
    }
