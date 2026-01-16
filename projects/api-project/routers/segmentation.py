"""
Segmentation API 라우터
세그먼트 정의 및 작업 관리
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from services.adobe_client import AdobeAPIClient

router = APIRouter()
client = AdobeAPIClient()


@router.get("/segment-definitions", summary="세그먼트 정의 목록 조회")
async def list_segment_definitions(
    limit: int = Query(10, ge=1, le=100, description="조회할 세그먼트 수"),
    page: int = Query(0, ge=0, description="페이지 번호")
):
    """
    모든 세그먼트 정의를 조회합니다.
    
    세그먼트 정의는 PQL(Profile Query Language)로 작성된 규칙입니다.
    
    - **limit**: 한 번에 조회할 세그먼트 수
    - **page**: 페이지 번호
    """
    try:
        segments = await client.get_segment_definitions(limit=limit, page=page)
        return segments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세그먼트 정의 목록 조회 실패: {str(e)}")


@router.get("/segment-definitions/{segment_id}", summary="특정 세그먼트 정의 조회")
async def get_segment_definition(segment_id: str):
    """
    특정 세그먼트 정의의 상세 정보를 조회합니다.
    
    - **segment_id**: 세그먼트 정의 ID
    """
    try:
        segment = await client.get_segment_definition(segment_id)
        return segment
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"세그먼트 정의 조회 실패: {str(e)}")


@router.get("/segment-jobs", summary="세그먼트 작업 목록 조회")
async def list_segment_jobs(
    limit: int = Query(10, ge=1, le=100, description="조회할 작업 수"),
    status: Optional[str] = Query(None, description="작업 상태 필터 (PROCESSING, SUCCEEDED, FAILED)")
):
    """
    세그먼트 평가 작업 목록을 조회합니다.
    
    세그먼트 작업은 세그먼트 정의를 실행하여 오디언스를 생성하는 프로세스입니다.
    
    - **limit**: 한 번에 조회할 작업 수
    - **status**: 작업 상태 필터
    """
    try:
        jobs = await client.get_segment_jobs(limit=limit, status=status)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세그먼트 작업 목록 조회 실패: {str(e)}")


@router.get("/segment-jobs/{job_id}", summary="특정 세그먼트 작업 조회")
async def get_segment_job(job_id: str):
    """
    특정 세그먼트 작업의 상태를 조회합니다.
    
    - **job_id**: 세그먼트 작업 ID
    """
    try:
        job = await client.get_segment_job(job_id)
        return job
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"세그먼트 작업 조회 실패: {str(e)}")


@router.get("/audiences", summary="오디언스 목록 조회")
async def list_audiences(
    limit: int = Query(10, ge=1, le=100, description="조회할 오디언스 수")
):
    """
    평가된 오디언스(세그먼트 결과) 목록을 조회합니다.
    
    오디언스는 세그먼트 정의를 평가한 결과로 생성된 프로필 집합입니다.
    """
    try:
        audiences = await client.get_audiences(limit=limit)
        return audiences
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오디언스 목록 조회 실패: {str(e)}")


@router.post("/segment-jobs", summary="세그먼트 작업 생성")
async def create_segment_job(segment_ids: List[str]):
    """
    새로운 세그먼트 평가 작업을 생성합니다.
    
    - **segment_ids**: 평가할 세그먼트 ID 목록
    """
    try:
        job = await client.create_segment_job(segment_ids)
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세그먼트 작업 생성 실패: {str(e)}")
