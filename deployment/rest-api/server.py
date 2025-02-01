"""FastAPI server for the Vortx API"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import yaml
from pathlib import Path

from .advanced_analysis import router as analysis_router
from .analysis_endpoints import router as basic_router
from .memory_endpoints import router as memory_router

def create_app(config: dict = None) -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="Vortx Earth Memory System API",
        description="API for satellite data processing and memory system",
        version="0.1.0",
        docs_url=None,
        redoc_url=None
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(analysis_router, prefix="/api/v1", tags=["Analysis"])
    app.include_router(basic_router, prefix="/api/v1", tags=["Processing"])
    app.include_router(memory_router, prefix="/api/v1/memory", tags=["Memory"])

    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        # Load custom OpenAPI schema
        openapi_path = Path(__file__).parent / "docs" / "openapi.yaml"
        with open(openapi_path) as f:
            openapi_schema = yaml.safe_load(f)

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="Vortx API Documentation",
            swagger_favicon_url="/static/favicon.ico"
        )

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}

    return app 