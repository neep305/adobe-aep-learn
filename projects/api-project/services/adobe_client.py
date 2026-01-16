"""
Adobe Experience Platform API 클라이언트
비동기 HTTP 클라이언트를 사용한 AEP API 호출
"""
import httpx
from typing import List, Optional, Dict, Any
from config import settings, get_aep_headers


class AdobeAPIClient:
    """Adobe Experience Platform API 클라이언트"""
    
    def __init__(self):
        self.base_url = settings.platform_gateway
        self.timeout = 30.0
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """공통 HTTP 요청 메서드"""
        url = f"{self.base_url}{endpoint}"
        headers = get_aep_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data
            )
            response.raise_for_status()
            return response.json()
    
    # Schema Registry API
    async def get_schemas(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """스키마 목록 조회"""
        params = {"limit": limit, "start": offset}
        result = await self._make_request("GET", "/data/foundation/schemaregistry/tenant/schemas", params=params)
        return result.get("results", [])
    
    async def get_schema(self, schema_id: str) -> Dict[str, Any]:
        """특정 스키마 조회"""
        return await self._make_request("GET", f"/data/foundation/schemaregistry/tenant/schemas/{schema_id}")
    
    async def get_classes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """클래스 목록 조회"""
        params = {"limit": limit}
        result = await self._make_request("GET", "/data/foundation/schemaregistry/global/classes", params=params)
        return result.get("results", [])
    
    async def get_field_groups(self, limit: int = 10, class_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """필드 그룹 목록 조회"""
        params = {"limit": limit}
        if class_id:
            params["property"] = f"meta:intendedToExtend=={class_id}"
        result = await self._make_request("GET", "/data/foundation/schemaregistry/global/fieldgroups", params=params)
        return result.get("results", [])
    
    async def get_data_types(self, limit: int = 10) -> List[Dict[str, Any]]:
        """데이터 타입 목록 조회"""
        params = {"limit": limit}
        result = await self._make_request("GET", "/data/foundation/schemaregistry/global/datatypes", params=params)
        return result.get("results", [])
    
    # Identity Service API
    async def get_identity_namespaces(self) -> List[Dict[str, Any]]:
        """Identity Namespace 목록 조회"""
        return await self._make_request("GET", "/data/core/idnamespace/identities")
    
    async def get_identity_namespace(self, namespace_id: int) -> Dict[str, Any]:
        """특정 Identity Namespace 조회"""
        return await self._make_request("GET", f"/data/core/idnamespace/identities/{namespace_id}")
    
    async def get_identity_graph(
        self,
        xid: Optional[str] = None,
        namespace: Optional[str] = None,
        identity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Identity Graph 조회"""
        params = {}
        if xid:
            params["xid"] = xid
        else:
            params["namespace"] = namespace
            params["nsid"] = identity_id
        return await self._make_request("GET", "/data/core/identity/cluster/members", params=params)
    
    async def get_cluster_members(
        self,
        xid: Optional[str] = None,
        namespace: Optional[str] = None,
        identity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """클러스터 멤버 조회"""
        return await self.get_identity_graph(xid, namespace, identity_id)
    
    # Profile API
    async def get_profile_entity(
        self,
        schema_name: str,
        entity_id: str,
        entity_id_ns: str,
        merge_policy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """프로필 엔티티 조회"""
        params = {
            "schema.name": schema_name,
            "entityId": entity_id,
            "entityIdNS": entity_id_ns
        }
        if merge_policy_id:
            params["mergePolicyId"] = merge_policy_id
        return await self._make_request("GET", "/data/core/ups/access/entities", params=params)
    
    async def get_merge_policies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Merge Policy 목록 조회"""
        params = {"limit": limit}
        result = await self._make_request("GET", "/data/core/ups/config/mergePolicies", params=params)
        return result.get("children", [])
    
    async def get_merge_policy(self, policy_id: str) -> Dict[str, Any]:
        """특정 Merge Policy 조회"""
        return await self._make_request("GET", f"/data/core/ups/config/mergePolicies/{policy_id}")
    
    async def preview_profiles(self, limit: int = 10) -> Dict[str, Any]:
        """프로필 미리보기"""
        params = {"limit": limit}
        return await self._make_request("GET", "/data/core/ups/preview", params=params)
    
    # Segmentation API
    async def get_segment_definitions(self, limit: int = 10, page: int = 0) -> Dict[str, Any]:
        """세그먼트 정의 목록 조회"""
        params = {"limit": limit, "page": page}
        return await self._make_request("GET", "/data/core/ups/segment/definitions", params=params)
    
    async def get_segment_definition(self, segment_id: str) -> Dict[str, Any]:
        """특정 세그먼트 정의 조회"""
        return await self._make_request("GET", f"/data/core/ups/segment/definitions/{segment_id}")
    
    async def get_segment_jobs(self, limit: int = 10, status: Optional[str] = None) -> Dict[str, Any]:
        """세그먼트 작업 목록 조회"""
        params = {"limit": limit}
        if status:
            params["status"] = status
        return await self._make_request("GET", "/data/core/ups/segment/jobs", params=params)
    
    async def get_segment_job(self, job_id: str) -> Dict[str, Any]:
        """특정 세그먼트 작업 조회"""
        return await self._make_request("GET", f"/data/core/ups/segment/jobs/{job_id}")
    
    async def get_audiences(self, limit: int = 10) -> Dict[str, Any]:
        """오디언스 목록 조회"""
        params = {"limit": limit}
        return await self._make_request("GET", "/data/core/ups/audiences", params=params)
    
    async def create_segment_job(self, segment_ids: List[str]) -> Dict[str, Any]:
        """세그먼트 작업 생성"""
        json_data = {"segmentId": segment_ids}
        return await self._make_request("POST", "/data/core/ups/segment/jobs", json_data=json_data)
    
    # Destinations API
    async def get_destinations(self, limit: int = 10) -> Dict[str, Any]:
        """대상 목록 조회"""
        params = {"limit": limit}
        return await self._make_request("GET", "/data/foundation/flowservice/destinations", params=params)
    
    async def get_destination(self, destination_id: str) -> Dict[str, Any]:
        """특정 대상 조회"""
        return await self._make_request("GET", f"/data/foundation/flowservice/destinations/{destination_id}")
    
    async def get_dataflows(self, limit: int = 10) -> Dict[str, Any]:
        """데이터 플로우 목록 조회"""
        params = {"limit": limit}
        return await self._make_request("GET", "/data/foundation/flowservice/flows", params=params)
    
    async def get_dataflow(self, dataflow_id: str) -> Dict[str, Any]:
        """특정 데이터 플로우 조회"""
        return await self._make_request("GET", f"/data/foundation/flowservice/flows/{dataflow_id}")
    
    async def get_dataflow_runs(self, dataflow_id: str, limit: int = 10) -> Dict[str, Any]:
        """데이터 플로우 실행 이력 조회"""
        params = {"property": f"flowId=={dataflow_id}", "limit": limit}
        return await self._make_request("GET", "/data/foundation/flowservice/runs", params=params)
    
    async def get_connection_specs(self) -> Dict[str, Any]:
        """연결 스펙 목록 조회"""
        return await self._make_request("GET", "/data/foundation/flowservice/connectionSpecs")
