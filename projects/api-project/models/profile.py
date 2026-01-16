"""
Real-Time Customer Profile 데이터 모델
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ProfileEntity(BaseModel):
    """프로필 엔티티 모델"""
    entity_id: str = Field(alias="entityId", description="엔티티 ID")
    entity: Dict[str, Any] = Field(description="프로필 데이터")
    lastModifiedAt: Optional[str] = Field(None, description="마지막 수정 시간")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "entityId": "id123",
                "entity": {
                    "person": {
                        "name": {
                            "firstName": "홍",
                            "lastName": "길동"
                        }
                    },
                    "personalEmail": {
                        "address": "hong@example.com"
                    }
                },
                "lastModifiedAt": "2024-01-15T10:30:00Z"
            }
        }


class MergePolicy(BaseModel):
    """Merge Policy 모델"""
    id: str = Field(description="Merge Policy ID")
    name: str = Field(description="Merge Policy 이름")
    description: Optional[str] = Field(None, description="설명")
    schema: Dict[str, str] = Field(description="스키마 정보")
    default: bool = Field(description="기본 정책 여부")
    identityGraph: Optional[Dict[str, Any]] = Field(None, description="Identity Graph 설정")
    attributeMerge: Optional[Dict[str, Any]] = Field(None, description="속성 병합 규칙")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "policy123",
                "name": "Default Timestamp Ordered",
                "description": "타임스탬프 기반 병합 정책",
                "schema": {
                    "name": "_xdm.context.profile"
                },
                "default": True,
                "identityGraph": {
                    "type": "none"
                },
                "attributeMerge": {
                    "type": "timestampOrdered"
                }
            }
        }


class ProfileQueryRequest(BaseModel):
    """프로필 조회 요청"""
    schema_name: str = Field(alias="schema.name", description="스키마 이름")
    entity_id: str = Field(alias="entityId", description="엔티티 ID")
    entity_id_ns: str = Field(alias="entityIdNS", description="엔티티 ID Namespace")
    merge_policy_id: Optional[str] = Field(None, alias="mergePolicyId", description="Merge Policy ID")
    
    class Config:
        populate_by_name = True
