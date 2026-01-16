"""
Adobe Experience Platform API Documentation Server
FastAPI 기반 AEP API 엔드포인트 문서화 및 테스트 서버
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import schema_registry, identity, profile, segmentation, destinations

app = FastAPI(
    title="Adobe Experience Platform API Documentation",
    description="""
    AEP(Adobe Experience Platform) API 엔드포인트를 정리하고 테스트할 수 있는 REST API 서버입니다.
    
    ## 주요 API 카테고리
    
    * **Schema Registry** - XDM 스키마 관리
    * **Identity Service** - Identity Graph 및 Namespace 관리
    * **Profile API** - Real-Time Customer Profile 조회
    * **Segmentation** - 세그먼트 정의 및 관리
    * **Destinations** - 데이터 활성화 대상 관리
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(schema_registry.router, prefix="/api/schema-registry", tags=["Schema Registry"])
app.include_router(identity.router, prefix="/api/identity", tags=["Identity Service"])
app.include_router(profile.router, prefix="/api/profile", tags=["Real-Time Customer Profile"])
app.include_router(segmentation.router, prefix="/api/segmentation", tags=["Segmentation"])
app.include_router(destinations.router, prefix="/api/destinations", tags=["Destinations"])


@app.get("/", tags=["Root"])
async def root():
    """API 서버 상태 확인"""
    return {
        "message": "Adobe Experience Platform API Documentation Server",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
