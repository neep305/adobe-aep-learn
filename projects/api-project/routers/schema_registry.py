"""
Schema Registry API 라우터
XDM 스키마, 클래스, 필드 그룹 관리
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.schema import SchemaModel, ClassModel, FieldGroupModel
from services.adobe_client import AdobeAPIClient

router = APIRouter()
client = AdobeAPIClient()


@router.get("/schemas", response_model=List[SchemaModel], summary="스키마 목록 조회")
async def list_schemas(
    limit: int = Query(10, ge=1, le=100, description="조회할 스키마 수"),
    offset: int = Query(0, ge=0, description="오프셋")
):
    """
    테넌트의 모든 XDM 스키마 목록을 조회합니다.
    
    - **limit**: 한 번에 조회할 스키마 수 (1-100)
    - **offset**: 페이지네이션 오프셋
    """
    try:
        schemas = await client.get_schemas(limit=limit, offset=offset)
        return schemas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스키마 목록 조회 실패: {str(e)}")


@router.get("/schemas/{schema_id}", response_model=SchemaModel, summary="특정 스키마 조회")
async def get_schema(schema_id: str):
    """
    특정 스키마의 상세 정보를 조회합니다.
    
    - **schema_id**: 스키마 ID (URL 인코딩 필요)
    """
    try:
        schema = await client.get_schema(schema_id)
        return schema
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"스키마 조회 실패: {str(e)}")


@router.get("/classes", response_model=List[ClassModel], summary="클래스 목록 조회")
async def list_classes(
    limit: int = Query(10, ge=1, le=100, description="조회할 클래스 수")
):
    """
    사용 가능한 XDM 클래스 목록을 조회합니다.
    
    주요 클래스:
    - XDM Individual Profile
    - XDM ExperienceEvent
    """
    try:
        classes = await client.get_classes(limit=limit)
        return classes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"클래스 목록 조회 실패: {str(e)}")


@router.get("/fieldgroups", response_model=List[FieldGroupModel], summary="필드 그룹 목록 조회")
async def list_field_groups(
    limit: int = Query(10, ge=1, le=100, description="조회할 필드 그룹 수"),
    class_id: Optional[str] = Query(None, description="특정 클래스에 속한 필드 그룹만 조회")
):
    """
    사용 가능한 필드 그룹 목록을 조회합니다.
    
    - **class_id**: 특정 클래스에 속한 필드 그룹만 필터링
    """
    try:
        field_groups = await client.get_field_groups(limit=limit, class_id=class_id)
        return field_groups
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"필드 그룹 목록 조회 실패: {str(e)}")


@router.get("/datatypes", summary="데이터 타입 목록 조회")
async def list_data_types(
    limit: int = Query(10, ge=1, le=100, description="조회할 데이터 타입 수")
):
    """
    사용 가능한 데이터 타입 목록을 조회합니다.
    """
    try:
        data_types = await client.get_data_types(limit=limit)
        return data_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 타입 목록 조회 실패: {str(e)}")
