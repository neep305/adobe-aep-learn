"""
Real-Time Customer Profile API 라우터
프로필 조회 및 Merge Policy 관리
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.profile import ProfileEntity, MergePolicy
from services.adobe_client import AdobeAPIClient

router = APIRouter()
client = AdobeAPIClient()


@router.get("/entities", response_model=ProfileEntity, summary="프로필 조회")
async def get_profile_entity(
    schema_name: str = Query("_xdm.context.profile", alias="schema.name", description="스키마 이름"),
    entity_id: str = Query(..., alias="entityId", description="엔티티 ID"),
    entity_id_ns: str = Query(..., alias="entityIdNS", description="엔티티 ID Namespace"),
    merge_policy_id: Optional[str] = Query(None, alias="mergePolicyId", description="Merge Policy ID")
):
    """
    특정 프로필의 통합된 뷰를 조회합니다.
    
    - **schema_name**: 스키마 이름 (기본값: _xdm.context.profile)
    - **entity_id**: 프로필 ID
    - **entity_id_ns**: ID Namespace (예: Email, ECID)
    - **merge_policy_id**: 사용할 Merge Policy (선택사항)
    
    예시:
    - `?entityId=user@example.com&entityIdNS=Email`
    - `?entityId=12345&entityIdNS=ECID&mergePolicyId=policy123`
    """
    try:
        profile = await client.get_profile_entity(
            schema_name=schema_name,
            entity_id=entity_id,
            entity_id_ns=entity_id_ns,
            merge_policy_id=merge_policy_id
        )
        return profile
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"프로필 조회 실패: {str(e)}")


@router.get("/merge-policies", response_model=List[MergePolicy], summary="Merge Policy 목록 조회")
async def list_merge_policies(
    limit: int = Query(10, ge=1, le=100, description="조회할 정책 수")
):
    """
    사용 가능한 모든 Merge Policy를 조회합니다.
    
    Merge Policy는 여러 데이터 소스의 프로필 데이터를 통합하는 규칙을 정의합니다.
    
    주요 병합 전략:
    - **Timestamp Ordered**: 타임스탬프 기반 병합
    - **Dataset Precedence**: 데이터셋 우선순위 기반 병합
    """
    try:
        policies = await client.get_merge_policies(limit=limit)
        return policies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merge Policy 목록 조회 실패: {str(e)}")


@router.get("/merge-policies/{policy_id}", response_model=MergePolicy, summary="특정 Merge Policy 조회")
async def get_merge_policy(policy_id: str):
    """
    특정 Merge Policy의 상세 정보를 조회합니다.
    
    - **policy_id**: Merge Policy ID
    """
    try:
        policy = await client.get_merge_policy(policy_id)
        return policy
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Merge Policy 조회 실패: {str(e)}")


@router.get("/preview", summary="프로필 미리보기")
async def preview_profiles(
    limit: int = Query(10, ge=1, le=50, description="조회할 프로필 수")
):
    """
    프로필 데이터를 미리보기합니다 (샘플링).
    
    실제 프로덕션 환경에서는 제한적으로 사용해야 합니다.
    """
    try:
        preview = await client.preview_profiles(limit=limit)
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 미리보기 실패: {str(e)}")
