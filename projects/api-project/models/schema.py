"""
XDM Schema Registry 데이터 모델
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SchemaModel(BaseModel):
    """XDM Schema 모델"""
    schema_id: str = Field(alias="$id", description="스키마 고유 ID")
    title: str = Field(description="스키마 제목")
    description: Optional[str] = Field(None, description="스키마 설명")
    type: str = Field(description="스키마 타입 (object)")
    version: str = Field(description="스키마 버전")
    meta: Optional[Dict[str, Any]] = Field(None, description="메타데이터")
    allOf: Optional[List[Dict[str, Any]]] = Field(None, description="상속된 스키마 및 필드 그룹")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "$id": "https://ns.adobe.com/tenant/schemas/example123",
                "title": "Customer Profile Schema",
                "description": "고객 프로필 정보 스키마",
                "type": "object",
                "version": "1.0"
            }
        }


class ClassModel(BaseModel):
    """XDM Class 모델"""
    class_id: str = Field(alias="$id", description="클래스 ID")
    title: str = Field(description="클래스 제목")
    description: Optional[str] = Field(None, description="클래스 설명")
    type: str = Field(description="클래스 타입")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "$id": "https://ns.adobe.com/xdm/context/profile",
                "title": "XDM Individual Profile",
                "description": "개인 프로필 클래스",
                "type": "object"
            }
        }


class FieldGroupModel(BaseModel):
    """Field Group 모델"""
    field_group_id: str = Field(alias="$id", description="필드 그룹 ID")
    title: str = Field(description="필드 그룹 제목")
    description: Optional[str] = Field(None, description="필드 그룹 설명")
    type: str = Field(description="필드 그룹 타입")
    meta: Optional[Dict[str, Any]] = Field(None, description="메타데이터")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "$id": "https://ns.adobe.com/xdm/context/profile-person-details",
                "title": "Profile Person Details",
                "description": "개인 상세 정보 필드 그룹",
                "type": "object"
            }
        }


class SchemaListResponse(BaseModel):
    """스키마 목록 응답"""
    results: List[SchemaModel]
    _page: Optional[Dict[str, Any]] = Field(None, description="페이지네이션 정보")
    _links: Optional[Dict[str, Any]] = Field(None, description="링크 정보")
