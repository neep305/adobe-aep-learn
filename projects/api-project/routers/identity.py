"""
Identity Service API 라우터
Identity Namespace 및 Identity Graph 관리
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from models.identity import IdentityNamespace, IdentityGraphResponse
from services.adobe_client import AdobeAPIClient

router = APIRouter()
client = AdobeAPIClient()


@router.get("/namespaces", response_model=List[IdentityNamespace], summary="Identity Namespace 목록 조회")
async def list_namespaces():
    """
    사용 가능한 모든 Identity Namespace를 조회합니다.
    
    주요 Namespace:
    - **ECID**: Experience Cloud ID
    - **Email**: 이메일 주소
    - **Phone**: 전화번호
    - **Custom**: 사용자 정의 Namespace
    """
    try:
        namespaces = await client.get_identity_namespaces()
        return namespaces
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Namespace 목록 조회 실패: {str(e)}")


@router.get("/namespaces/{namespace_id}", response_model=IdentityNamespace, summary="특정 Namespace 조회")
async def get_namespace(namespace_id: int):
    """
    특정 Identity Namespace의 상세 정보를 조회합니다.
    
    - **namespace_id**: Namespace ID (숫자)
    """
    try:
        namespace = await client.get_identity_namespace(namespace_id)
        return namespace
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Namespace 조회 실패: {str(e)}")


@router.get("/identity-graph", response_model=IdentityGraphResponse, summary="Identity Graph 조회")
async def get_identity_graph(
    xid: str = Query(None, description="Experience Cloud ID"),
    namespace: str = Query(None, description="Identity Namespace 코드"),
    identity_id: str = Query(None, alias="id", description="Identity 값")
):
    """
    특정 Identity와 연결된 Identity Graph를 조회합니다.
    
    다음 중 하나의 조합으로 조회 가능:
    - **xid**: Experience Cloud ID만 사용
    - **namespace + identity_id**: Namespace 코드와 Identity 값 조합
    
    예시:
    - `?xid=CJKdkdkdj8dkjKJS`
    - `?namespace=Email&id=user@example.com`
    """
    if not xid and not (namespace and identity_id):
        raise HTTPException(
            status_code=400,
            detail="xid 또는 (namespace + id) 조합이 필요합니다"
        )
    
    try:
        graph = await client.get_identity_graph(
            xid=xid,
            namespace=namespace,
            identity_id=identity_id
        )
        return graph
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Identity Graph 조회 실패: {str(e)}")


@router.get("/cluster-members", summary="클러스터 멤버 조회")
async def get_cluster_members(
    xid: str = Query(None, description="Experience Cloud ID"),
    namespace: str = Query(None, description="Identity Namespace 코드"),
    identity_id: str = Query(None, alias="id", description="Identity 값")
):
    """
    Identity Cluster의 모든 멤버를 조회합니다.
    """
    if not xid and not (namespace and identity_id):
        raise HTTPException(
            status_code=400,
            detail="xid 또는 (namespace + id) 조합이 필요합니다"
        )
    
    try:
        members = await client.get_cluster_members(
            xid=xid,
            namespace=namespace,
            identity_id=identity_id
        )
        return members
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"클러스터 멤버 조회 실패: {str(e)}")
