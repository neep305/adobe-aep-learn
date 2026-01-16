"""
Identity Service 데이터 모델
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class IdentityNamespace(BaseModel):
    """Identity Namespace 모델"""
    id: int = Field(description="Namespace ID")
    name: str = Field(description="Namespace 이름")
    code: str = Field(description="Namespace 코드")
    description: Optional[str] = Field(None, description="설명")
    idType: str = Field(description="ID 타입 (COOKIE, EMAIL, PHONE, etc.)")
    namespaceType: str = Field(description="Namespace 타입 (Standard, Custom)")
    createTime: Optional[int] = Field(None, description="생성 시간 (timestamp)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 4,
                "name": "Email",
                "code": "Email",
                "description": "이메일 주소",
                "idType": "EMAIL",
                "namespaceType": "Standard",
                "createTime": 1551688425000
            }
        }


class Identity(BaseModel):
    """Identity 정보"""
    namespace: str = Field(description="Identity Namespace")
    id: str = Field(description="Identity 값")


class IdentityGraphResponse(BaseModel):
    """Identity Graph 조회 응답"""
    identities: List[Identity] = Field(description="연결된 Identity 목록")
    xid: Optional[str] = Field(None, description="Experience Cloud ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "identities": [
                    {"namespace": "ECID", "id": "12345"},
                    {"namespace": "Email", "id": "user@example.com"},
                    {"namespace": "Phone", "id": "+821012345678"}
                ],
                "xid": "CJKdkdkdj8dkjKJS"
            }
        }


class IdentityGraphRequest(BaseModel):
    """Identity Graph 조회 요청"""
    xid: Optional[str] = Field(None, description="Experience Cloud ID")
    namespace_code: Optional[str] = Field(None, alias="namespace.code", description="Namespace 코드")
    namespace_id: Optional[str] = Field(None, alias="namespace.id", description="Identity ID")
    
    class Config:
        populate_by_name = True
