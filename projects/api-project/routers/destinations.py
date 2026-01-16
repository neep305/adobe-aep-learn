"""
Destinations API 라우터
데이터 활성화 대상 관리
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from services.adobe_client import AdobeAPIClient

router = APIRouter()
client = AdobeAPIClient()


@router.get("/destinations", summary="대상 목록 조회")
async def list_destinations(
    limit: int = Query(10, ge=1, le=100, description="조회할 대상 수")
):
    """
    사용 가능한 모든 대상(Destination)을 조회합니다.
    
    대상 유형:
    - **스트리밍 대상**: 실시간 데이터 전송
    - **배치 대상**: 정기적인 파일 전송
    - **프로필 대상**: 프로필 기반 활성화
    - **세그먼트 대상**: 세그먼트 기반 활성화
    """
    try:
        destinations = await client.get_destinations(limit=limit)
        return destinations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대상 목록 조회 실패: {str(e)}")


@router.get("/destinations/{destination_id}", summary="특정 대상 조회")
async def get_destination(destination_id: str):
    """
    특정 대상의 상세 정보를 조회합니다.
    
    - **destination_id**: 대상 ID
    """
    try:
        destination = await client.get_destination(destination_id)
        return destination
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"대상 조회 실패: {str(e)}")


@router.get("/dataflows", summary="데이터 플로우 목록 조회")
async def list_dataflows(
    limit: int = Query(10, ge=1, le=100, description="조회할 데이터 플로우 수")
):
    """
    활성 데이터 플로우 목록을 조회합니다.
    
    데이터 플로우는 AEP에서 대상으로 데이터를 전송하는 파이프라인입니다.
    """
    try:
        dataflows = await client.get_dataflows(limit=limit)
        return dataflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 플로우 목록 조회 실패: {str(e)}")


@router.get("/dataflows/{dataflow_id}", summary="특정 데이터 플로우 조회")
async def get_dataflow(dataflow_id: str):
    """
    특정 데이터 플로우의 상세 정보를 조회합니다.
    
    - **dataflow_id**: 데이터 플로우 ID
    """
    try:
        dataflow = await client.get_dataflow(dataflow_id)
        return dataflow
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"데이터 플로우 조회 실패: {str(e)}")


@router.get("/dataflows/{dataflow_id}/runs", summary="데이터 플로우 실행 이력 조회")
async def list_dataflow_runs(
    dataflow_id: str,
    limit: int = Query(10, ge=1, le=100, description="조회할 실행 이력 수")
):
    """
    특정 데이터 플로우의 실행 이력을 조회합니다.
    
    - **dataflow_id**: 데이터 플로우 ID
    - **limit**: 조회할 실행 이력 수
    """
    try:
        runs = await client.get_dataflow_runs(dataflow_id, limit=limit)
        return runs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 플로우 실행 이력 조회 실패: {str(e)}")


@router.get("/connection-specs", summary="연결 스펙 목록 조회")
async def list_connection_specs():
    """
    사용 가능한 연결 스펙(Connection Spec) 목록을 조회합니다.
    
    연결 스펙은 외부 시스템과의 연결 방법을 정의합니다.
    
    주요 연결 스펙:
    - Google Ads
    - Facebook Ads
    - HTTP API
    - Email Marketing Platforms
    """
    try:
        specs = await client.get_connection_specs()
        return specs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연결 스펙 목록 조회 실패: {str(e)}")
